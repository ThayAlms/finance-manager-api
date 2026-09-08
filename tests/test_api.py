from datetime import date, timedelta
from decimal import Decimal

from tests.conftest import register_and_login


def test_health_and_openapi(client):
    assert client.get("/health").json() == {"status": "UP"}
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "CaixaLivre API"
    assert "/api/v1/transacoes" in document["paths"]
    assert document["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"


def test_openapi_is_documented(client):
    """Trava a qualidade do Swagger: endpoint novo sem descricao quebra aqui.

    Sem este teste a documentacao apodrece em silencio — o FastAPI inventa um
    summary a partir do nome da funcao ("Create", "Delete") e ninguem percebe
    ate alguem abrir o /docs.
    """
    document = client.get("/openapi.json").json()

    operacoes = [
        (metodo, rota, corpo)
        for rota, metodos in document["paths"].items()
        for metodo, corpo in metodos.items()
    ]
    assert len(operacoes) >= 26

    sem_summary = [
        f"{m.upper()} {r}" for m, r, c in operacoes if not c.get("summary")
    ]
    sem_descricao = [
        f"{m.upper()} {r}" for m, r, c in operacoes if not c.get("description")
    ]
    assert sem_summary == [], f"operacoes sem summary: {sem_summary}"
    assert sem_descricao == [], f"operacoes sem description: {sem_descricao}"

    # Summary gerado pelo FastAPI a partir do nome da funcao nao serve.
    genericos = {"Create", "Update", "Delete", "Find", "List All", "Get Me"}
    inventados = [
        f"{m.upper()} {r}" for m, r, c in operacoes if c["summary"] in genericos
    ]
    assert inventados == [], f"summary generico do FastAPI: {inventados}"

    # Toda tag usada precisa estar descrita na raiz do documento.
    descritas = {tag["name"] for tag in document["tags"]}
    usadas = {tag for _, _, corpo in operacoes for tag in corpo.get("tags", [])}
    assert usadas <= descritas, f"tags sem descricao: {usadas - descritas}"

    # Schemas de contrato precisam de exemplo; enum nao, ja lista seus valores.
    schemas = document["components"]["schemas"]
    sem_exemplo = [
        nome
        for nome, corpo in schemas.items()
        if "enum" not in corpo and "example" not in corpo
    ]
    assert sem_exemplo == [], f"schemas sem exemplo: {sem_exemplo}"


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


def test_summary_splits_personal_and_business(client, auth_headers):
    """O caso que a RN14 permite e que o resumo precisa mostrar: despesa do
    negocio paga pela conta pessoal. O saldo cai na conta pessoal, mas a
    despesa conta como do negocio."""
    categories = client.get("/api/v1/categorias", headers=auth_headers).json()
    income_category = next(item for item in categories if item["tipo"] == "RECEITA")
    expense_category = next(item for item in categories if item["tipo"] == "DESPESA")

    accounts = {}
    for nome, natureza, saldo in (
        ("Conta pessoal", "PESSOAL", "1000.00"),
        ("Conta do negocio", "NEGOCIO", "2000.00"),
    ):
        created = client.post(
            "/api/v1/contas",
            headers=auth_headers,
            json={
                "nome": nome,
                "tipo": "CORRENTE",
                "natureza": natureza,
                "saldo_inicial": saldo,
            },
        )
        assert created.status_code == 201, created.text
        accounts[natureza] = created.json()["id"]

    hoje = date.today()
    lancamentos = (
        # Receita do negocio na conta do negocio.
        (accounts["NEGOCIO"], income_category, "RECEITA", "NEGOCIO", "800.00"),
        # Despesa pessoal na conta pessoal.
        (accounts["PESSOAL"], expense_category, "DESPESA", "PESSOAL", "150.00"),
        # O caso da RN14: despesa do negocio paga pela conta pessoal.
        (accounts["PESSOAL"], expense_category, "DESPESA", "NEGOCIO", "100.00"),
    )
    for conta_id, categoria, tipo, natureza, valor in lancamentos:
        created = client.post(
            "/api/v1/transacoes",
            headers=auth_headers,
            json={
                "conta_id": conta_id,
                "categoria_id": categoria["id"],
                "descricao": "Lancamento de teste",
                "valor": valor,
                "data": hoje.isoformat(),
                "tipo": tipo,
                "natureza": natureza,
            },
        )
        assert created.status_code == 201, created.text

    response = client.get("/api/v1/resumo", headers=auth_headers)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["mes"] == hoje.month and body["ano"] == hoje.year
    assert body["quantidade_transacoes"] == 3
    # 1000 + 2000 + 800 - 150 - 100
    assert body["saldo_total"] == "3550.00"
    assert body["total_receitas"] == "800.00"
    assert body["total_despesas"] == "250.00"
    assert body["economia"] == "550.00"

    por_natureza = {linha["natureza"]: linha for linha in body["por_natureza"]}
    pessoal, negocio = por_natureza["PESSOAL"], por_natureza["NEGOCIO"]

    # Saldo segue a CONTA: as duas despesas sairam da conta pessoal.
    assert pessoal["saldo_contas"] == "750.00"
    assert negocio["saldo_contas"] == "2800.00"
    # Despesa segue a TRANSACAO: a de 100,00 e do negocio, mesmo saindo dali.
    assert pessoal["total_despesas"] == "150.00"
    assert negocio["total_despesas"] == "100.00"
    assert negocio["total_receitas"] == "800.00"
    assert pessoal["economia"] == "-150.00"
    assert negocio["economia"] == "700.00"


def test_summary_is_isolated_empty_and_validated(client, auth_headers):
    outro_token = register_and_login(client, "vizinho@example.com")
    outro_headers = {"Authorization": f"Bearer {outro_token}"}

    created = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={
            "nome": "Conta unica",
            "tipo": "CARTEIRA",
            "natureza": "PESSOAL",
            "saldo_inicial": "500.00",
        },
    )
    assert created.status_code == 201, created.text

    # RN01: o resumo do vizinho nao enxerga a conta de ninguem.
    vizinho = client.get("/api/v1/resumo", headers=outro_headers).json()
    assert vizinho["saldo_total"] == "0.00"
    assert vizinho["quantidade_transacoes"] == 0
    assert {linha["natureza"] for linha in vizinho["por_natureza"]} == {"PESSOAL", "NEGOCIO"}

    # Mes sem lancamento devolve zeros, nao lista vazia nem 404.
    passado = client.get(
        "/api/v1/resumo", headers=auth_headers, params={"mes": 1, "ano": 2020}
    ).json()
    assert passado["inicio"] == "2020-01-01" and passado["fim"] == "2020-01-31"
    assert passado["total_receitas"] == "0.00"
    # Saldo e acumulado, nao do periodo: aparece mesmo num mes sem transacao.
    assert passado["saldo_total"] == "500.00"

    # Fevereiro bissexto: o ultimo dia sai de monthrange, nao de tabela fixa.
    bissexto = client.get(
        "/api/v1/resumo", headers=auth_headers, params={"mes": 2, "ano": 2024}
    ).json()
    assert bissexto["fim"] == "2024-02-29"

    assert client.get("/api/v1/resumo").status_code == 401
    assert (
        client.get("/api/v1/resumo", headers=auth_headers, params={"mes": 13}).status_code
        == 422
    )


def test_transaction_filters_combine_and_agree_with_summary(client, auth_headers):
    """Os filtros se acumulam, e o recorte por natureza usa o mesmo criterio
    do /resumo — o total filtrado tem que bater com o total resumido."""
    categories = client.get("/api/v1/categorias", headers=auth_headers).json()
    income_category = next(item for item in categories if item["tipo"] == "RECEITA")
    expense_category = next(item for item in categories if item["tipo"] == "DESPESA")

    conta = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={
            "nome": "Conta pessoal",
            "tipo": "CORRENTE",
            "natureza": "PESSOAL",
            "saldo_inicial": "0.00",
        },
    )
    assert conta.status_code == 201, conta.text
    conta_id = conta.json()["id"]

    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    lancamentos = (
        (income_category, "RECEITA", "PESSOAL", "300.00", hoje),
        (income_category, "RECEITA", "NEGOCIO", "800.00", hoje),
        (expense_category, "DESPESA", "PESSOAL", "150.00", hoje),
        # Despesa do negocio paga pela conta pessoal (RN14).
        (expense_category, "DESPESA", "NEGOCIO", "100.00", ontem),
    )
    for categoria, tipo, natureza, valor, quando in lancamentos:
        created = client.post(
            "/api/v1/transacoes",
            headers=auth_headers,
            json={
                "conta_id": conta_id,
                "categoria_id": categoria["id"],
                "descricao": "Lancamento de teste",
                "valor": valor,
                "data": quando.isoformat(),
                "tipo": tipo,
                "natureza": natureza,
            },
        )
        assert created.status_code == 201, created.text

    def listar(**filtros):
        resposta = client.get("/api/v1/transacoes", headers=auth_headers, params=filtros)
        assert resposta.status_code == 200, resposta.text
        return resposta.json()

    # Sem filtro nenhum: historico completo.
    assert len(listar()) == 4

    # Um filtro de cada vez.
    assert len(listar(tipo="RECEITA")) == 2
    assert len(listar(tipo="DESPESA")) == 2
    assert len(listar(natureza="PESSOAL")) == 2
    assert len(listar(natureza="NEGOCIO")) == 2

    # Os filtros se acumulam.
    apenas = listar(tipo="DESPESA", natureza="NEGOCIO")
    assert len(apenas) == 1
    assert apenas[0]["valor"] == "100.00"

    # E se acumulam tambem com o periodo: a despesa do negocio foi ontem.
    assert listar(tipo="DESPESA", natureza="NEGOCIO", inicio=hoje.isoformat()) == []
    assert len(listar(tipo="DESPESA", natureza="NEGOCIO", inicio=ontem.isoformat())) == 1

    # Combinacao sem resultado devolve lista vazia com 200, nao 404.
    assert listar(tipo="RECEITA", natureza="PESSOAL", inicio=ontem.isoformat(), fim=ontem.isoformat()) == []

    # Coerencia com o /resumo: a despesa do negocio saiu da conta PESSOAL,
    # mas os dois endpoints a contam como do negocio.
    resumo = client.get(
        "/api/v1/resumo",
        headers=auth_headers,
        params={"mes": hoje.month, "ano": hoje.year},
    ).json()
    por_natureza = {linha["natureza"]: linha for linha in resumo["por_natureza"]}
    if hoje.month == ontem.month:
        despesas_negocio = listar(
            tipo="DESPESA",
            natureza="NEGOCIO",
            inicio=resumo["inicio"],
            fim=resumo["fim"],
        )
        somado = sum(
            (Decimal(item["valor"]) for item in despesas_negocio), Decimal("0.00")
        )
        assert somado == Decimal(por_natureza["NEGOCIO"]["total_despesas"])

    # Valor fora do enum e recusado antes de chegar ao banco.
    assert (
        client.get(
            "/api/v1/transacoes", headers=auth_headers, params={"tipo": "INVESTIMENTO"}
        ).status_code
        == 422
    )


def test_delete_is_blocked_by_ownership_and_links(client, auth_headers):
    """As tres travas de exclusao: 403 na categoria de sistema (RN09) e 409
    em conta (RN10) e categoria (RN08) que ainda tem transacao."""
    categorias = client.get("/api/v1/categorias", headers=auth_headers).json()
    sistema = next(item for item in categorias if item["sistema"])

    # RN09: categoria de sistema e uma linha so, compartilhada por todos.
    # Editar ou excluir afetaria os outros usuarios, entao e 403 e nao 404 —
    # o recurso e publico, o usuario sabe que existe, falta e permissao.
    alterar = client.put(
        f"/api/v1/categorias/{sistema['id']}",
        headers=auth_headers,
        json={"nome": "Rango", "tipo": sistema["tipo"]},
    )
    assert alterar.status_code == 403, alterar.text
    excluir = client.delete(f"/api/v1/categorias/{sistema['id']}", headers=auth_headers)
    assert excluir.status_code == 403, excluir.text

    # Categoria pessoal sem uso: exclusao permitida.
    propria = client.post(
        "/api/v1/categorias",
        headers=auth_headers,
        json={"nome": "Assinaturas", "tipo": "DESPESA"},
    )
    assert propria.status_code == 201, propria.text
    propria_id = propria.json()["id"]
    assert propria.json()["sistema"] is False
    assert client.delete(f"/api/v1/categorias/{propria_id}", headers=auth_headers).status_code == 204

    # Agora com transacao vinculada, as duas exclusoes passam a ser bloqueadas.
    categoria = client.post(
        "/api/v1/categorias",
        headers=auth_headers,
        json={"nome": "Ferramentas", "tipo": "DESPESA"},
    ).json()
    conta = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={"nome": "Conta com uso", "tipo": "CORRENTE", "natureza": "NEGOCIO"},
    ).json()
    transacao = client.post(
        "/api/v1/transacoes",
        headers=auth_headers,
        json={
            "conta_id": conta["id"],
            "categoria_id": categoria["id"],
            "descricao": "Licenca de software",
            "valor": "49.90",
            "data": date.today().isoformat(),
            "tipo": "DESPESA",
        },
    )
    assert transacao.status_code == 201, transacao.text

    # RN10: apagar em cascata sumiria com o historico financeiro sem aviso.
    conta_bloqueada = client.delete(f"/api/v1/contas/{conta['id']}", headers=auth_headers)
    assert conta_bloqueada.status_code == 409
    assert "1" in conta_bloqueada.json()["message"]

    # RN08: mesma logica — o usuario precisa reclassificar antes.
    categoria_bloqueada = client.delete(
        f"/api/v1/categorias/{categoria['id']}", headers=auth_headers
    )
    assert categoria_bloqueada.status_code == 409
    assert "1" in categoria_bloqueada.json()["message"]

    # Removida a transacao, as duas exclusoes voltam a ser aceitas.
    assert client.delete(
        f"/api/v1/transacoes/{transacao.json()['id']}", headers=auth_headers
    ).status_code == 204
    assert client.delete(f"/api/v1/contas/{conta['id']}", headers=auth_headers).status_code == 204
    assert client.delete(
        f"/api/v1/categorias/{categoria['id']}", headers=auth_headers
    ).status_code == 204


def test_duplicates_and_foreign_links_are_rejected(client, auth_headers):
    """RN15 (nome de categoria unico por usuario e tipo) e RN06 (conta e
    categoria da transacao precisam ser do usuario do token)."""
    primeira = client.post(
        "/api/v1/categorias",
        headers=auth_headers,
        json={"nome": "Transporte", "tipo": "DESPESA"},
    )
    assert primeira.status_code == 201

    # Mesmo nome e mesmo tipo, so trocando a caixa: e duplicata (RN15).
    duplicada = client.post(
        "/api/v1/categorias",
        headers=auth_headers,
        json={"nome": "transporte", "tipo": "DESPESA"},
    )
    assert duplicada.status_code == 409, duplicada.text

    # Mesmo nome em tipo diferente e permitido de proposito: transporte como
    # despesa (combustivel) e como receita (o frete cobrado do cliente).
    outro_tipo = client.post(
        "/api/v1/categorias",
        headers=auth_headers,
        json={"nome": "Transporte", "tipo": "RECEITA"},
    )
    assert outro_tipo.status_code == 201, outro_tipo.text

    # Conta duplicada tambem e 409.
    conta = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={"nome": "Carteira", "tipo": "CARTEIRA", "natureza": "PESSOAL"},
    )
    assert conta.status_code == 201
    repetida = client.post(
        "/api/v1/contas",
        headers=auth_headers,
        json={"nome": "carteira", "tipo": "CORRENTE", "natureza": "NEGOCIO"},
    )
    assert repetida.status_code == 409, repetida.text

    # RN06: o vizinho nao consegue lancar na conta alheia nem passando o id.
    vizinho = {"Authorization": f"Bearer {register_and_login(client, 'vizinho2@example.com')}"}
    invasao = client.post(
        "/api/v1/transacoes",
        headers=vizinho,
        json={
            "conta_id": conta.json()["id"],
            "categoria_id": primeira.json()["id"],
            "descricao": "Tentativa",
            "valor": "10.00",
            "data": date.today().isoformat(),
            "tipo": "DESPESA",
        },
    )
    assert invasao.status_code == 404, invasao.text
