from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.routers import accounts, auth, categories, dashboard, goals, health, insights, transactions, users
from app.schemas.common import COMMON_RESPONSES

app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST do CaixaLivre para separar e controlar as finanças pessoais "
        "e do negócio de autônomos, freelancers e MEIs."
    ),
    version="1.0.0",
    contact={"name": "Equipe CaixaLivre"},
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

app.include_router(health.router)

for api_router in (
    auth.router,
    users.router,
    categories.router,
    accounts.router,
    transactions.router,
    goals.router,
    dashboard.router,
    insights.router,
):
    app.include_router(
        api_router,
        prefix="/api/v1",
        responses=COMMON_RESPONSES,
    )
