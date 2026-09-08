from pydantic import ConfigDict, Field

from app.models.enums import TipoMovimento
from app.schemas.common import SchemaBase


class CategoriaCreate(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={"example": {"nome": "Combustível", "tipo": "DESPESA"}}
    )

    nome: str = Field(
        min_length=1,
        max_length=60,
        description="Único por usuário dentro do mesmo tipo, ignorando maiúsculas (RN15).",
    )
    tipo: TipoMovimento = Field(
        description="Define quais transações podem usar esta categoria (RN05)."
    )


class CategoriaResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 7, "nome": "Combustível", "tipo": "DESPESA", "sistema": False}
        }
    )

    id: int
    nome: str
    tipo: TipoMovimento
    sistema: bool = Field(
        description=(
            "`true` para as categorias do seed, compartilhadas por todos os "
            "usuários e somente leitura (RN09 e RN16)."
        )
    )
