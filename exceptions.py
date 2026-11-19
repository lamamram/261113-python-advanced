from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any
class ArticleNotFoundException(Exception):
    def __init__(self, article_id: int):
        self.article_id = article_id

class BadTokenException(Exception):
    ...

def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(ArticleNotFoundException)
    async def article_not_found_handler(request: Request, exc: ArticleNotFoundException):
        return JSONResponse(
            status_code=404,
            content={
                "erreur": "ARTICLE_NOT_FOUND",
                "message": f"L'article {exc.article_id} n'existe pas",
                "code": 404,
            },
        )

    @app.exception_handler(BadTokenException)
    async def bad_token_handler(request: Request, exc: BadTokenException):
        return JSONResponse(
            status_code=401,
            content={
                "erreur": "UNAUTHORIZED",
                "message": "Le token fourni est invalide",
                "code": 401,
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "erreur": "VALIDATION_ERROR",
                "message": "Certains champs ne sont pas valides",
                "details": exc.errors(),
                "code": 422,
            },
        )