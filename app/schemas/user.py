from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field

from app.schemas.common import SchemaBase


class UsuarioCreate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Maria Silva",
                "email": "maria@email.com",
                "senha": "Senha@123",
            }
        }
    )

    nome: str = Field(min_length=1, max_length=120, description="Nome de exibição.")
    email: EmailStr = Field(
        max_length=180,
        description="Serve de login. Único, ignorando maiúsculas (RN02).",
    )
    senha: str = Field(
        min_length=8,
        max_length=72,
        description=(
            "Mínimo de 8 caracteres. Guardada apenas como hash bcrypt e nunca "
            "devolvida em nenhuma resposta (RN03). O teto de 72 é o limite do "
            "próprio bcrypt, que ignora o que passa disso."
        ),
    )


class UsuarioUpdate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"nome": "Maria Silva Souza", "email": "maria.souza@email.com"}
        }
    )

    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=180)


class UsuarioResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nome": "Maria Silva",
                "email": "maria@email.com",
                "criado_em": "2026-09-07T18:00:00-03:00",
            }
        }
    )

    id: int
    nome: str
    email: str = Field(description="Sempre normalizado em minúsculas.")
    criado_em: datetime
