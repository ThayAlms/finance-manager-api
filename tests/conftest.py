import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Categoria, TipoMovimento

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def override_get_db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    with TestingSession() as session:
        session.add_all(
            [
                Categoria(nome="Serviços prestados", tipo=TipoMovimento.RECEITA),
                Categoria(nome="Alimentação", tipo=TipoMovimento.DESPESA),
            ]
        )
        session.commit()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/v1/usuarios",
        json={"nome": "Pessoa Teste", "email": email, "senha": "Senha@123"},
    )
    assert response.status_code == 201, response.text
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "Senha@123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(client: TestClient):
    token = register_and_login(client, "usuario@example.com")
    return {"Authorization": f"Bearer {token}"}
