from datetime import date, timedelta

from tests.conftest import register_and_login


def test_health_and_openapi(client):
    assert client.get("/health").json() == {"status": "UP"}
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "CaixaLivre API"
    assert "/api/v1/transacoes" in document["paths"]
    assert document["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"


def test_registration_login_and_protected_profile(client):
    payload = {"nome": "Maria Silva", "email": "MARIA@EMAIL.COM", "senha": "Senha@123"}
    created = client.post("/api/v1/usuarios", json=payload)
    assert created.status_code == 201
    assert created.json()["email"] == "maria@email.com"
    assert "senha" not in created.json()

    duplicate = client.post("/api/v1/usuarios", json=payload)
    assert duplicate.status_code == 409

    assert client.get("/api/v1/usuarios/me").status_code == 401
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "maria@email.com", "senha": "Senha@123"},
    ).json()["access_token"]
    profile = client.get(
        "/api/v1/usuarios/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.json()["nome"] == "Maria Silva"


def test_financial_workflow_and_calculated_balance(client, auth_headers):
    categories = client.get("/api/v1/categorias", headers=auth_headers).json()
    income_category = next(item for item in categories if item["tipo"] == "RECEITA")
    expense_category = next(item for item in categories if item["tipo"] == "DESPESA")
    assert income_category["sistema"] is True

    account = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={
            "nome": "Conta PJ",
            "tipo": "CORRENTE",
            "natureza": "NEGOCIO",
            "saldo_inicial": "1000.00",
        },
    )
    assert account.status_code == 201, account.text
    account_id = account.json()["id"]

    for category, movement_type, value in (
        (income_category, "RECEITA", "500.00"),
        (expense_category, "DESPESA", "200.00"),
    ):
        response = client.post(
            "/api/v1/transacoes",
            headers=auth_headers,
            json={
                "conta_id": account_id,
                "categoria_id": category["id"],
                "descricao": "Movimento de teste",
                "valor": value,
                "data": date.today().isoformat(),
                "tipo": movement_type,
            },
        )
        assert response.status_code == 201, response.text
        assert response.json()["natureza"] == "NEGOCIO"

    account = client.get(f"/api/v1/contas/{account_id}", headers=auth_headers)
    assert account.json()["saldo_atual"] == "1300.00"

    blocked = client.delete(f"/api/v1/contas/{account_id}", headers=auth_headers)
    assert blocked.status_code == 409
    assert "2 transação(ões)" in blocked.json()["message"]


def test_transaction_rules(client, auth_headers):
    category = client.get("/api/v1/categorias", headers=auth_headers).json()[0]
    account_id = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={"nome": "Carteira", "tipo": "CARTEIRA", "natureza": "PESSOAL"},
    ).json()["id"]
    base = {
        "conta_id": account_id,
        "categoria_id": category["id"],
        "descricao": "Inválida",
        "valor": "10.00",
        "data": date.today().isoformat(),
        "tipo": category["tipo"],
    }

    future = client.post(
        "/api/v1/transacoes",
        headers=auth_headers,
        json={**base, "data": (date.today() + timedelta(days=1)).isoformat()},
    )
    assert future.status_code == 422

    opposite = "DESPESA" if category["tipo"] == "RECEITA" else "RECEITA"
    incompatible = client.post(
        "/api/v1/transacoes",
        headers=auth_headers,
        json={**base, "tipo": opposite},
    )
    assert incompatible.status_code == 422

    negative = client.post(
        "/api/v1/transacoes", headers=auth_headers, json={**base, "valor": "-1.00"}
    )
    assert negative.status_code == 422
    assert "valor" in negative.json()["fieldErrors"]


def test_user_cannot_access_another_users_account(client, auth_headers):
    account_id = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={"nome": "Privada", "tipo": "CORRENTE", "natureza": "PESSOAL"},
    ).json()["id"]

    other_token = register_and_login(client, "outro@example.com")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    response = client.get(f"/api/v1/contas/{account_id}", headers=other_headers)
    assert response.status_code == 404


def test_goal_calculations(client, auth_headers):
    response = client.post(
        "/api/v1/metas",
        headers=auth_headers,
        json={"nome": "Reserva", "valor_meta": "1000.00", "valor_atual": "1200.00"},
    )
    assert response.status_code == 201
    assert response.json()["valor_restante"] == "0.00"
    assert response.json()["progresso_percentual"] == "100.00"
    assert response.json()["atingida"] is True


def test_dashboard_summary_filters_and_pagination(client, auth_headers):
    categories = client.get("/api/v1/categorias", headers=auth_headers).json()
    income = next(item for item in categories if item["tipo"] == "RECEITA")
    expense = next(item for item in categories if item["tipo"] == "DESPESA")
    account = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={
            "nome": "Conta do dashboard",
            "tipo": "CORRENTE",
            "natureza": "NEGOCIO",
            "saldo_inicial": "100.00",
        },
    ).json()
    for category, movement_type, amount in (
        (income, "RECEITA", "1000.00"),
        (expense, "DESPESA", "250.00"),
    ):
        response = client.post(
            "/api/v1/transacoes",
            headers=auth_headers,
            json={
                "conta_id": account["id"],
                "categoria_id": category["id"],
                "descricao": f"Movimento {movement_type}",
                "valor": amount,
                "data": date.today().isoformat(),
                "tipo": movement_type,
            },
        )
        assert response.status_code == 201

    query = f"inicio={date.today().replace(day=1)}&fim={date.today()}"
    summary = client.get(f"/api/v1/resumo?{query}", headers=auth_headers)
    assert summary.status_code == 200, summary.text
    assert summary.json()["receitas"] == "1000.00"
    assert summary.json()["despesas"] == "250.00"
    assert summary.json()["resultado"] == "750.00"
    assert summary.json()["saldo_total"] == "850.00"
    assert summary.json()["taxa_economia"] == "75.00"
    assert summary.json()["por_natureza"][1]["natureza"] == "NEGOCIO"
    assert len(summary.json()["evolucao_mensal"]) == 1

    filtered = client.get(
        f"/api/v1/transacoes?{query}&tipo=DESPESA&limit=1",
        headers=auth_headers,
    )
    assert filtered.status_code == 200
    assert filtered.headers["X-Total-Count"] == "1"
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["tipo"] == "DESPESA"


def test_insight_uses_safe_local_fallback_without_api_key(client, auth_headers):
    query = f"inicio={date.today().replace(day=1)}&fim={date.today()}"
    response = client.post(f"/api/v1/insights?{query}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["gerado_por_ia"] is False
    assert "OPENAI_API_KEY" in response.json()["aviso"]


def test_insight_reads_text_from_responses_api(client, auth_headers, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "model": "modelo-teste",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "Mantenha seu planejamento mensal."}
                        ],
                    }
                ],
            }

    monkeypatch.setattr("app.services.insight.settings.openai_api_key", "chave-teste")
    monkeypatch.setattr("app.services.insight.httpx.post", lambda *args, **kwargs: FakeResponse())
    query = f"inicio={date.today().replace(day=1)}&fim={date.today()}"
    response = client.post(f"/api/v1/insights?{query}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {
        "insight": "Mantenha seu planejamento mensal.",
        "gerado_por_ia": True,
        "modelo": "modelo-teste",
        "aviso": None,
    }


def test_case_insensitive_account_and_goal_names_are_unique(client, auth_headers):
    account = {
        "nome": "Conta Principal",
        "tipo": "CORRENTE",
        "natureza": "PESSOAL",
    }
    assert client.post("/api/v1/contas", headers=auth_headers, json=account).status_code == 201
    duplicate_account = client.post(
        "/api/v1/contas", headers=auth_headers, json={**account, "nome": "conta principal"}
    )
    assert duplicate_account.status_code == 409

    goal = {"nome": "Reserva", "valor_meta": "5000.00"}
    assert client.post("/api/v1/metas", headers=auth_headers, json=goal).status_code == 201
    duplicate_goal = client.post(
        "/api/v1/metas", headers=auth_headers, json={**goal, "nome": "reserva"}
    )
    assert duplicate_goal.status_code == 409
