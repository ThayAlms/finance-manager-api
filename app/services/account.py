from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.models import Conta, Usuario
from app.repositories import account as repository
from app.repositories import transaction as transaction_repository
from app.schemas import ContaCreate, ContaResponse, ContaUpdate


def response(
    session: Session, item: Conta, saldo_atual=None
) -> ContaResponse:
    return ContaResponse(
        id=item.id,
        nome=item.nome,
        tipo=item.tipo,
        natureza=item.natureza,
        saldo_inicial=item.saldo_inicial,
        saldo_atual=(
            repository.current_balance(session, item)
            if saldo_atual is None
            else saldo_atual
        ),
        criado_em=item.criado_em,
    )


def find(session: Session, conta_id: int, usuario: Usuario) -> Conta:
    item = repository.by_id_for_user(session, conta_id, usuario.id)
    if item is None:
        not_found("Conta não encontrada")
    return item


def list_all(session: Session, usuario: Usuario) -> list[ContaResponse]:
    return [
        response(session, item, saldo)
        for item, saldo in repository.all_with_balance_by_user(session, usuario.id)
    ]


def create(session: Session, usuario: Usuario, request: ContaCreate) -> ContaResponse:
    nome = request.nome.strip()
    if repository.duplicate(session, usuario.id, nome):
        conflict("Já existe uma conta com este nome")
    item = Conta(
        usuario_id=usuario.id,
        nome=nome,
        tipo=request.tipo,
        natureza=request.natureza,
        saldo_inicial=request.saldo_inicial,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return response(session, item)


def update(
    session: Session, usuario: Usuario, conta_id: int, request: ContaUpdate
) -> ContaResponse:
    item = find(session, conta_id, usuario)
    nome = request.nome.strip()
    if repository.duplicate(session, usuario.id, nome, item.id):
        conflict("Já existe uma conta com este nome")
    item.nome = nome
    item.tipo = request.tipo
    item.natureza = request.natureza
    session.commit()
    session.refresh(item)
    return response(session, item)


def delete(session: Session, usuario: Usuario, conta_id: int) -> None:
    item = find(session, conta_id, usuario)
    count = transaction_repository.count_by_account(session, item.id)
    if count:
        conflict(f"A conta possui {count} transação(ões) vinculada(s)")
    session.delete(item)
    session.commit()
