from sqlalchemy.orm import Session

from app.core.errors import conflict, forbidden, not_found
from app.models import Categoria, Usuario
from app.repositories import category as repository
from app.repositories import transaction as transaction_repository
from app.schemas import CategoriaCreate, CategoriaResponse


def response(item: Categoria) -> CategoriaResponse:
    return CategoriaResponse(
        id=item.id,
        nome=item.nome,
        tipo=item.tipo,
        sistema=item.usuario_id is None,
    )


def find(session: Session, categoria_id: int, usuario: Usuario) -> Categoria:
    item = repository.by_id_visible(session, categoria_id, usuario.id)
    if item is None:
        not_found("Categoria não encontrada")
    return item


def list_all(session: Session, usuario: Usuario) -> list[CategoriaResponse]:
    return [response(item) for item in repository.visible_to(session, usuario.id)]


def create(
    session: Session, usuario: Usuario, request: CategoriaCreate
) -> CategoriaResponse:
    nome = request.nome.strip()
    if repository.duplicate(session, usuario.id, nome, request.tipo):
        conflict("Já existe uma categoria com este nome e tipo")
    item = Categoria(usuario_id=usuario.id, nome=nome, tipo=request.tipo)
    session.add(item)
    session.commit()
    session.refresh(item)
    return response(item)


def update(
    session: Session, usuario: Usuario, categoria_id: int, request: CategoriaCreate
) -> CategoriaResponse:
    item = find(session, categoria_id, usuario)
    if item.usuario_id is None:
        forbidden("Categorias de sistema não podem ser alteradas")
    nome = request.nome.strip()
    if repository.duplicate(session, usuario.id, nome, request.tipo, item.id):
        conflict("Já existe uma categoria com este nome e tipo")
    item.nome = nome
    item.tipo = request.tipo
    session.commit()
    session.refresh(item)
    return response(item)


def delete(session: Session, usuario: Usuario, categoria_id: int) -> None:
    item = find(session, categoria_id, usuario)
    if item.usuario_id is None:
        forbidden("Categorias de sistema não podem ser excluídas")
    count = transaction_repository.count_by_category(session, item.id)
    if count:
        conflict(f"A categoria possui {count} transação(ões) vinculada(s)")
    session.delete(item)
    session.commit()
