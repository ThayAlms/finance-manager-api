from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import SchemaBase


class UsuarioCreate(SchemaBase):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=180)
    senha: str = Field(min_length=8, max_length=72)


class UsuarioUpdate(SchemaBase):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=180)


class UsuarioResponse(SchemaBase):
    id: int
    nome: str
    email: str
    criado_em: datetime
