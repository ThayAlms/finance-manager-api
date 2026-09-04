from app.models.enums import TipoMovimento
from app.schemas.common import SchemaBase
from pydantic import Field


class CategoriaCreate(SchemaBase):
    nome: str = Field(min_length=1, max_length=60)
    tipo: TipoMovimento


class CategoriaResponse(SchemaBase):
    id: int
    nome: str
    tipo: TipoMovimento
    sistema: bool
