import csv
import base64
import binascii
import hashlib
import io
import json
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import not_found, unprocessable
from app.models import Categoria, Conta, Natureza, TipoMovimento, Transacao, Usuario
from app.repositories import account as account_repository
from app.repositories import category as category_repository
from app.repositories import transaction as transaction_repository
from app.schemas import (
    ExtratoConfirmRequest,
    ExtratoConfirmResponse,
    ExtratoPreviewRequest,
    ExtratoPreviewResponse,
    LancamentoImportacao,
)

DATE_HEADERS = {"data", "date", "dtposted", "data lancamento", "data movimento"}
DESCRIPTION_HEADERS = {
    "descricao",
    "description",
    "historico",
    "memo",
    "nome",
    "lancamento",
}
AMOUNT_HEADERS = {"valor", "amount", "trnamt", "montante", "quantia"}
CREDIT_HEADERS = {"credito", "credit", "entrada", "receita"}
DEBIT_HEADERS = {"debito", "debit", "saida", "despesa"}
MAX_PDF_BYTES = 10_000_000


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return " ".join(
        "".join(character for character in normalized if not unicodedata.combining(character))
        .replace("_", " ")
        .split()
    )


def _parse_date(value: str) -> date:
    clean = value.strip()[:10]
    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y%m%d"):
        try:
            return datetime.strptime(clean, pattern).date()
        except ValueError:
            continue
    raise ValueError(f"Data inválida: {value}")


def _parse_money(value: str) -> Decimal:
    clean = value.strip().replace("R$", "").replace(" ", "")
    negative_parentheses = clean.startswith("(") and clean.endswith(")")
    clean = clean.strip("()")
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    try:
        amount = Decimal(clean)
    except InvalidOperation as exc:
        raise ValueError(f"Valor inválido: {value}") from exc
    return -amount if negative_parentheses else amount


def _first(row: dict[str, str], names: set[str]) -> str:
    for key, value in row.items():
        if _normalize(key) in names and value and value.strip():
            return value.strip()
    return ""


def _csv_entries(content: str) -> list[dict]:
    sample = content[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("O CSV não possui cabeçalho")

    entries = []
    for line_number, row in enumerate(reader, start=2):
        raw_date = _first(row, DATE_HEADERS)
        description = _first(row, DESCRIPTION_HEADERS)
        amount_text = _first(row, AMOUNT_HEADERS)
        if not amount_text:
            credit = _first(row, CREDIT_HEADERS)
            debit = _first(row, DEBIT_HEADERS)
            amount_text = credit or debit
            if debit:
                amount_text = f"-{amount_text.lstrip('-')}"
        if not raw_date and not description and not amount_text:
            continue
        if not raw_date or not description or not amount_text:
            raise ValueError(
                f"Linha {line_number}: data, descrição e valor são obrigatórios"
            )
        entries.append(
            {
                "linha": line_number,
                "data": _parse_date(raw_date),
                "descricao": description[:160],
                "valor_assinado": _parse_money(amount_text),
            }
        )
    return entries


def _ofx_tag(block: str, name: str) -> str:
    match = re.search(rf"<{name}>\s*([^<\r\n]+)", block, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _ofx_entries(content: str) -> list[dict]:
    blocks = re.findall(
        r"<STMTTRN>(.*?)(?:</STMTTRN>|(?=<STMTTRN>)|$)",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    entries = []
    for line_number, block in enumerate(blocks, start=1):
        raw_date = _ofx_tag(block, "DTPOSTED")[:8]
        amount = _ofx_tag(block, "TRNAMT")
        description = _ofx_tag(block, "MEMO") or _ofx_tag(block, "NAME")
        if raw_date and amount and description:
            entries.append(
                {
                    "linha": line_number,
                    "data": _parse_date(raw_date),
                    "descricao": description[:160],
                    "valor_assinado": _parse_money(amount),
                }
            )
    return entries


def _fingerprint(entry: dict) -> str:
    canonical = "|".join(
        (
            entry["data"].isoformat(),
            _normalize(entry["descricao"]),
            f"{entry['valor_assinado']:.2f}",
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _default_category(entry: dict, categories: list[Categoria]) -> Categoria:
    movement_type = (
        TipoMovimento.RECEITA
        if entry["valor_assinado"] > 0
        else TipoMovimento.DESPESA
    )
    description = _normalize(entry["descricao"])
    keywords = {
        "aliment": "Alimentação",
        "mercado": "Alimentação",
        "uber": "Transporte",
        "combust": "Transporte",
        "farmacia": "Saúde",
        "software": "Ferramentas e software",
        "imposto": "Impostos e taxas",
        "salario": "Salário",
        "servico": "Serviços prestados",
        "venda": "Vendas",
    }
    preferred = next(
        (name for keyword, name in keywords.items() if keyword in description),
        "Outras receitas"
        if movement_type == TipoMovimento.RECEITA
        else "Outras despesas",
    )
    return next(
        (
            category
            for category in categories
            if category.tipo == movement_type
            and _normalize(category.nome) == _normalize(preferred)
        ),
        next(category for category in categories if category.tipo == movement_type),
    )


def _default_nature(description: str, default: Natureza) -> Natureza:
    business_terms = (
        "cnpj",
        "mei",
        "nota fiscal",
        "cliente",
        "fornecedor",
        "maquininha",
        "pro labore",
        "servico prestado",
    )
    normalized = _normalize(description)
    return (
        Natureza.NEGOCIO
        if any(term in normalized for term in business_terms)
        else default
    )


def _gemini_classification(
    entries: list[dict], categories: list[Categoria], default: Natureza
) -> tuple[dict[int, dict], bool, str | None, str | None]:
    if not settings.gemini_api_key:
        return {}, False, None, "GEMINI_API_KEY não configurada; regras locais utilizadas."

    allowed = [
        {"id": category.id, "nome": category.nome, "tipo": category.tipo.value}
        for category in categories
    ]
    items = [
        {
            "linha": entry["linha"],
            "data": entry["data"].isoformat(),
            "descricao": entry["descricao"],
            "valor": str(abs(entry["valor_assinado"])),
            "tipo": (
                TipoMovimento.RECEITA.value
                if entry["valor_assinado"] > 0
                else TipoMovimento.DESPESA.value
            ),
        }
        for entry in entries
    ]
    instructions = (
        "Classifique lançamentos bancários brasileiros. NEGOCIO significa atividade "
        "profissional, MEI ou pessoa jurídica; PESSOAL significa vida particular. "
        "Escolha somente um categoria_id fornecido e compatível com o tipo. Não "
        "invente informações. Quando houver dúvida, use a natureza padrão e confiança baixa."
    )
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "linha": {"type": "integer"},
                "natureza": {"type": "string", "enum": ["PESSOAL", "NEGOCIO"]},
                "categoria_id": {"type": "integer"},
                "confianca": {"type": "number"},
                "justificativa": {"type": "string"},
            },
            "required": [
                "linha",
                "natureza",
                "categoria_id",
                "confianca",
                "justificativa",
            ],
        },
    }
    payload = {
        "system_instruction": {"parts": [{"text": instructions}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": json.dumps(
                            {
                                "natureza_padrao": default.value,
                                "categorias_permitidas": allowed,
                                "lancamentos": items,
                            },
                            ensure_ascii=False,
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
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
        text = "".join(
            part.get("text", "")
            for candidate in body.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        )
        classified = json.loads(text)
        return (
            {int(item["linha"]): item for item in classified},
            True,
            body.get("modelVersion", settings.gemini_model),
            None,
        )
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return {}, False, None, "Gemini indisponível; regras locais utilizadas."


def _gemini_pdf_extraction(
    encoded_pdf: str, categories: list[Categoria], default: Natureza
) -> tuple[list[dict], dict[int, dict], str]:
    if not settings.gemini_api_key:
        unprocessable(
            "A importação de PDF requer GEMINI_API_KEY; use CSV/OFX para análise local"
        )
    try:
        pdf_bytes = base64.b64decode(encoded_pdf, validate=True)
    except (binascii.Error, ValueError):
        unprocessable("O conteúdo do PDF não está em base64 válido")
    if len(pdf_bytes) > MAX_PDF_BYTES:
        unprocessable("O PDF pode ter no máximo 10 MB")
    if not pdf_bytes.startswith(b"%PDF-"):
        unprocessable("O arquivo enviado não possui uma assinatura PDF válida")

    allowed = [
        {"id": category.id, "nome": category.nome, "tipo": category.tipo.value}
        for category in categories
    ]
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "data": {"type": "string"},
                "descricao": {"type": "string"},
                "valor_assinado": {"type": "number"},
                "natureza": {"type": "string", "enum": ["PESSOAL", "NEGOCIO"]},
                "categoria_id": {"type": "integer"},
                "confianca": {"type": "number"},
                "justificativa": {"type": "string"},
            },
            "required": [
                "data",
                "descricao",
                "valor_assinado",
                "natureza",
                "categoria_id",
                "confianca",
                "justificativa",
            ],
        },
    }
    prompt = {
        "tarefa": (
            "Extraia todos os lançamentos reais deste extrato bancário brasileiro. "
            "Ignore saldo anterior/final, totais, gráficos, cabeçalhos e notas. Não "
            "duplique linhas. Use valor positivo para crédito/entrada e negativo para "
            "débito/saída. Datas devem ser YYYY-MM-DD; quando o ano estiver apenas no "
            "cabeçalho, aplique-o aos lançamentos. Classifique também cada lançamento: "
            "NEGOCIO para atividade profissional, MEI ou pessoa jurídica e PESSOAL "
            "para vida particular. Não invente dados ilegíveis."
        ),
        "natureza_padrao": default.value,
        "categorias_permitidas": allowed,
        "regra_categoria": "Use somente um id fornecido e compatível com crédito/débito.",
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "application/pdf",
                            "data": encoded_pdf,
                        }
                    },
                    {"text": json.dumps(prompt, ensure_ascii=False)},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
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
        text = "".join(
            part.get("text", "")
            for candidate in body.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        )
        extracted = json.loads(text)
        entries: list[dict] = []
        classifications: dict[int, dict] = {}
        for line, item in enumerate(extracted, start=1):
            amount = Decimal(str(item["valor_assinado"]))
            if amount == 0:
                continue
            normalized_line = len(entries) + 1
            entries.append(
                {
                    "linha": normalized_line,
                    "data": _parse_date(str(item["data"])),
                    "descricao": str(item["descricao"]).strip()[:160],
                    "valor_assinado": amount,
                }
            )
            classifications[normalized_line] = {
                "natureza": item["natureza"],
                "categoria_id": item["categoria_id"],
                "confianca": item["confianca"],
                "justificativa": item["justificativa"],
            }
        return entries, classifications, body.get(
            "modelVersion", settings.gemini_model
        )
    except (httpx.HTTPError, ValueError, KeyError, TypeError, InvalidOperation):
        unprocessable(
            "Não foi possível analisar o PDF com o Gemini. Confira a chave e tente novamente"
        )


def preview(
    session: Session, usuario: Usuario, request: ExtratoPreviewRequest
) -> ExtratoPreviewResponse:
    extension = request.arquivo_nome.rsplit(".", 1)[-1].lower()
    categories = category_repository.visible_to(session, usuario.id)
    ai_items: dict[int, dict] = {}
    generated_by_ai = False
    model = None
    warning = None
    try:
        if extension == "csv":
            if request.codificacao != "texto":
                raise ValueError("CSV deve ser enviado como texto")
            entries = _csv_entries(request.conteudo)
        elif extension in {"ofx", "qfx"}:
            if request.codificacao != "texto":
                raise ValueError("OFX/QFX deve ser enviado como texto")
            entries = _ofx_entries(request.conteudo)
        elif extension == "pdf":
            if request.codificacao != "base64":
                raise ValueError("PDF deve ser enviado em base64")
            entries, ai_items, model = _gemini_pdf_extraction(
                request.conteudo, categories, request.natureza_padrao
            )
            generated_by_ai = True
        else:
            unprocessable("Formato não suportado. Envie CSV, OFX, QFX ou PDF")
    except (csv.Error, UnicodeError, ValueError) as exc:
        unprocessable(f"Não foi possível ler o extrato: {exc}")

    if not entries:
        unprocessable("Nenhum lançamento válido foi encontrado no extrato")
    if len(entries) > 500:
        unprocessable("O extrato pode conter no máximo 500 lançamentos")

    account = account_repository.by_name_for_user(
        session, request.conta_nome, usuario.id
    )
    hashes = [_fingerprint(entry) for entry in entries]
    duplicates = (
        transaction_repository.imported_hashes(session, account.id, hashes)
        if account
        else set()
    )
    if extension != "pdf":
        ai_items, generated_by_ai, model, warning = _gemini_classification(
            entries, categories, request.natureza_padrao
        )
    categories_by_id = {category.id: category for category in categories}

    result = []
    for entry, fingerprint in zip(entries, hashes, strict=True):
        movement_type = (
            TipoMovimento.RECEITA
            if entry["valor_assinado"] > 0
            else TipoMovimento.DESPESA
        )
        fallback_category = _default_category(entry, categories)
        ai_item = ai_items.get(entry["linha"], {})
        selected_category = categories_by_id.get(ai_item.get("categoria_id"))
        if selected_category is None or selected_category.tipo != movement_type:
            selected_category = fallback_category
        try:
            nature = Natureza(ai_item.get("natureza"))
        except ValueError:
            nature = _default_nature(entry["descricao"], request.natureza_padrao)
        confidence = Decimal(str(ai_item.get("confianca", "0.55")))
        confidence = max(Decimal("0"), min(confidence, Decimal("1")))
        result.append(
            LancamentoImportacao(
                linha=entry["linha"],
                data=entry["data"],
                descricao=entry["descricao"],
                valor=abs(entry["valor_assinado"]),
                tipo=movement_type,
                natureza=nature,
                categoria_id=selected_category.id,
                categoria_nome=selected_category.nome,
                confianca=confidence,
                justificativa=str(
                    ai_item.get(
                        "justificativa", "Classificação baseada em regras locais"
                    )
                )[:240],
                fingerprint=fingerprint,
                duplicada=fingerprint in duplicates,
            )
        )

    return ExtratoPreviewResponse(
        arquivo_nome=request.arquivo_nome,
        conta_existente_id=account.id if account else None,
        conta_nome=request.conta_nome,
        tipo_conta=account.tipo if account else request.tipo_conta,
        natureza_padrao=account.natureza if account else request.natureza_padrao,
        total_linhas=len(result),
        total_creditos=sum(
            (item.valor for item in result if item.tipo == TipoMovimento.RECEITA),
            Decimal("0.00"),
        ),
        total_debitos=sum(
            (item.valor for item in result if item.tipo == TipoMovimento.DESPESA),
            Decimal("0.00"),
        ),
        classificado_por_ia=generated_by_ai,
        modelo=model,
        aviso=warning,
        lancamentos=result,
    )


def confirm(
    session: Session, usuario: Usuario, request: ExtratoConfirmRequest
) -> ExtratoConfirmResponse:
    if request.conta_id is not None:
        account = account_repository.by_id_for_user(
            session, request.conta_id, usuario.id
        )
        if account is None:
            not_found("Conta não encontrada")
    else:
        account = account_repository.by_name_for_user(
            session, request.conta_nome, usuario.id
        )
        if account is None:
            account = Conta(
                usuario_id=usuario.id,
                nome=request.conta_nome.strip(),
                tipo=request.tipo_conta,
                natureza=request.natureza,
                saldo_inicial=request.saldo_inicial,
            )
            session.add(account)
            session.flush()

    categories = {
        category.id: category
        for category in category_repository.visible_to(session, usuario.id)
    }
    hashes = [item.fingerprint for item in request.lancamentos]
    existing = transaction_repository.imported_hashes(session, account.id, hashes)
    imported = 0
    skipped = 0
    seen = set(existing)
    for item in request.lancamentos:
        if item.duplicada or item.fingerprint in seen:
            skipped += 1
            continue
        category = categories.get(item.categoria_id)
        if category is None or category.tipo != item.tipo:
            unprocessable(
                f"Linha {item.linha}: categoria inválida para o tipo da transação"
            )
        session.add(
            Transacao(
                conta=account,
                categoria=category,
                descricao=item.descricao.strip(),
                valor=item.valor,
                data=item.data,
                tipo=item.tipo,
                natureza=item.natureza,
                import_hash=item.fingerprint,
            )
        )
        seen.add(item.fingerprint)
        imported += 1
    session.commit()
    return ExtratoConfirmResponse(
        conta_id=account.id,
        conta_nome=account.nome,
        importadas=imported,
        ignoradas_duplicadas=skipped,
    )
