from pydantic import ConfigDict, EmailStr, Field

from app.schemas.common import SchemaBase


class LoginRequest(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "maria@email.com", "senha": "Senha@123"}
        }
    )

    email: EmailStr = Field(max_length=180)
    senha: str = Field(min_length=8, max_length=72)


class TokenResponse(SchemaBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.PAYLOAD.ASSINATURA",
                "token_type": "bearer",
            }
        }
    )

    access_token: str = Field(
        description="Envie em `Authorization: Bearer SEU_TOKEN`. Expira em 60 minutos."
    )
    token_type: str = "bearer"
