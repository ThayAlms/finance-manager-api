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
