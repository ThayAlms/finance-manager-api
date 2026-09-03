from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class ApiException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def not_found(message: str) -> None:
    raise ApiException(404, message)


def forbidden(message: str) -> None:
    raise ApiException(403, message)


def conflict(message: str) -> None:
    raise ApiException(409, message)


def unprocessable(message: str) -> None:
    raise ApiException(422, message)


def _body(request: Request, status_code: int, message: str, field_errors=None) -> dict:
    labels = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }
    body = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status_code,
        "error": labels.get(status_code, "Error"),
        "message": message,
        "path": request.url.path,
    }
    if field_errors:
        body["fieldErrors"] = field_errors
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(request, exc.status_code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        malformed_json = any(error["type"] == "json_invalid" for error in exc.errors())
        if malformed_json:
            return JSONResponse(
                status_code=400,
                content=_body(request, 400, "JSON malformado"),
            )
        fields = {
            ".".join(str(item) for item in error["loc"] if item != "body"): error["msg"]
            for error in exc.errors()
        }
        return JSONResponse(
            status_code=422,
            content=_body(
                request,
                422,
                "Existem campos inválidos na requisição",
                fields,
            ),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=409,
            content=_body(request, 409, "A operação viola uma restrição dos dados"),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=_body(request, 500, "Ocorreu um erro interno inesperado"),
        )
