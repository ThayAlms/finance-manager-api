from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.models import Meta, Usuario
from app.repositories import goal as repository
from app.schemas import MetaCreate, MetaResponse


def response(item: Meta) -> MetaResponse:
    remaining = max(item.valor_meta - item.valor_atual, Decimal("0.00"))
    progress = (
        item.valor_atual / item.valor_meta * Decimal("100")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return MetaResponse(
        id=item.id,
        nome=item.nome,
        valor_meta=item.valor_meta,
        valor_atual=item.valor_atual,
        valor_restante=remaining,
        progresso_percentual=min(progress, Decimal("100.00")),
        atingida=item.valor_atual >= item.valor_meta,
        prazo=item.prazo,
        criado_em=item.criado_em,
    )


def find(session: Session, meta_id: int, usuario: Usuario) -> Meta:
    item = repository.by_id_for_user(session, meta_id, usuario.id)
    if item is None:
        not_found("Meta não encontrada")
    return item


def list_all(session: Session, usuario: Usuario) -> list[MetaResponse]:
    return [response(item) for item in repository.all_by_user(session, usuario.id)]


def create(session: Session, usuario: Usuario, request: MetaCreate) -> MetaResponse:
    dados = request.model_dump()
    dados["nome"] = dados["nome"].strip()
    if repository.duplicate(session, usuario.id, dados["nome"]):
        conflict("Já existe uma meta com este nome")
    item = Meta(usuario_id=usuario.id, **dados)
    session.add(item)
    session.commit()
    session.refresh(item)
    return response(item)


def update(
    session: Session, usuario: Usuario, meta_id: int, request: MetaCreate
) -> MetaResponse:
    item = find(session, meta_id, usuario)
    dados = request.model_dump()
    dados["nome"] = dados["nome"].strip()
    if repository.duplicate(session, usuario.id, dados["nome"], item.id):
        conflict("Já existe uma meta com este nome")
    for field, value in dados.items():
        setattr(item, field, value)
    session.commit()
    session.refresh(item)
    return response(item)


def delete(session: Session, usuario: Usuario, meta_id: int) -> None:
    item = find(session, meta_id, usuario)
    session.delete(item)
    session.commit()
