from pydantic import EmailStr, Field

from app.schemas.common import SchemaBase


class LoginRequest(SchemaBase):
    email: EmailStr = Field(max_length=180)
    senha: str = Field(min_length=8, max_length=72)


class TokenResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
