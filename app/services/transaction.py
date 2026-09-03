from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import not_found, unprocessable
from app.models import Transacao, Usuario
from app.repositories import transaction as repository
from app.schemas import TransacaoCreate, TransacaoResponse
from app.services import account as account_service
from app.services import category as category_service


def response(item: Transacao) -> TransacaoResponse:
    return TransacaoResponse(
        id=item.id,
        conta_id=item.conta_id,
        conta_nome=item.conta.nome,
        categoria_id=item.categoria_id,
        categoria_nome=item.categoria.nome,
        descricao=item.descricao,
        valor=item.valor,
        data=item.data,
        tipo=item.tipo,
        natureza=item.natureza,
        criado_em=item.criado_em,
    )


def validate(request: TransacaoCreate, conta, categoria) -> None:
    if request.data > date.today():
        unprocessable("A data da transação não pode estar no futuro")
    if categoria.tipo != request.tipo:
        unprocessable("O tipo da transação deve ser igual ao tipo da categoria")


def find(session: Session, transacao_id: int, usuario: Usuario) -> Transacao:
    item = repository.by_id_for_user(session, transacao_id, usuario.id)
    if item is None:
        not_found("Transação não encontrada")
    return item


def list_all(
    session: Session, usuario: Usuario, inicio: date, fim: date
) -> list[TransacaoResponse]:
    if inicio > fim:
        unprocessable("A data inicial não pode ser posterior à data final")
    return [response(item) for item in repository.all_by_user(session, usuario.id, inicio, fim)]


def create(
    session: Session, usuario: Usuario, request: TransacaoCreate
) -> TransacaoResponse:
    conta = account_service.find(session, request.conta_id, usuario)
    categoria = category_service.find(session, request.categoria_id, usuario)
    validate(request, conta, categoria)
    item = Transacao(
        conta=conta,
        categoria=categoria,
        descricao=request.descricao.strip(),
        valor=request.valor,
        data=request.data,
        tipo=request.tipo,
        natureza=request.natureza or conta.natureza,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return response(item)


def update(
    session: Session,
    usuario: Usuario,
    transacao_id: int,
    request: TransacaoCreate,
) -> TransacaoResponse:
    item = find(session, transacao_id, usuario)
    conta = account_service.find(session, request.conta_id, usuario)
    categoria = category_service.find(session, request.categoria_id, usuario)
    validate(request, conta, categoria)
    item.conta = conta
    item.categoria = categoria
    item.descricao = request.descricao.strip()
    item.valor = request.valor
    item.data = request.data
    item.tipo = request.tipo
    item.natureza = request.natureza or conta.natureza
    session.commit()
    session.refresh(item)
    return response(item)


def delete(session: Session, usuario: Usuario, transacao_id: int) -> None:
    item = find(session, transacao_id, usuario)
    session.delete(item)
    session.commit()
