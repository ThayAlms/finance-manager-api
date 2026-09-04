from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import LoginRequest, TokenResponse
from app.services import auth as service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse, summary="Autenticar usuário")
def login(request: LoginRequest, session: Session = Depends(get_db)) -> TokenResponse:
    return service.login(session, request)
