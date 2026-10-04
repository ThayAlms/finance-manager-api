import json

import httpx

from app.core.config import settings
from app.schemas.dashboard import InsightResponse, ResumoResponse

INSTRUCTIONS = """Você é um assistente de educação financeira do CaixaLivre.
Analise somente os números agregados fornecidos. Responda em português do Brasil,
em até 120 palavras, com três observações práticas e objetivas. Não invente dados,
não prometa resultados, não dê recomendação de investimento e deixe claro que a
análise é educativa, não aconselhamento financeiro profissional."""


def _fallback(summary: ResumoResponse, warning: str) -> InsightResponse:
    if summary.receitas == 0 and summary.despesas == 0:
        text = "Ainda não há movimentações no período. Registre receitas e despesas para receber uma análise financeira."
    elif summary.resultado < 0:
        text = (
            f"As despesas superaram as receitas em R$ {abs(summary.resultado):.2f}. "
            "Revise primeiro as maiores categorias de despesa e defina um limite mensal."
        )
    else:
        text = (
            f"O período terminou positivo em R$ {summary.resultado:.2f}, com taxa de economia "
            f"de {summary.taxa_economia:.2f}%. Mantenha o acompanhamento por categoria e natureza."
        )
    return InsightResponse(insight=text, gerado_por_ia=False, aviso=warning)


def generate(summary: ResumoResponse) -> InsightResponse:
    if not settings.gemini_api_key:
        return _fallback(summary, "GEMINI_API_KEY não configurada; análise local utilizada.")

    payload = {
        "system_instruction": {"parts": [{"text": INSTRUCTIONS}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": json.dumps(
                            summary.model_dump(mode="json"), ensure_ascii=False
                        )
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 300},
    }
    try:
        response = httpx.post(
            (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{settings.gemini_model}:generateContent"
            ),
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=settings.gemini_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        texts = [
            part.get("text", "")
            for candidate in body.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
            if "text" in part
        ]
        insight = "\n".join(text for text in texts if text).strip()
        if not insight:
            return _fallback(summary, "A IA não retornou conteúdo; análise local utilizada.")
        return InsightResponse(
            insight=insight,
            gerado_por_ia=True,
            modelo=body.get("modelVersion", settings.gemini_model),
        )
    except (httpx.HTTPError, ValueError, KeyError):
        return _fallback(summary, "Serviço de IA indisponível; análise local utilizada.")
