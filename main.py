# main.py
from fastapi import FastAPI, Request
# -- optimisation de fastapi pour importer un module depuis un package
from routers import articles
from exceptions import ArticleNonTrouveException
from fastapi.responses import JSONResponse


app = FastAPI(
    title="API Catalogue",
    description="Premier projet FastAPI — formation Dawan",
    version="0.1.0",
)

@app.exception_handler(ArticleNonTrouveException)
async def article_not_found_handler(request: Request, exc: ArticleNonTrouveException):
    return JSONResponse(
        status_code=404,
        content={
            "erreur": "ARTICLE_NOT_FOUND",
            "message": f"L'article {exc.article_id} n'existe pas",
            "code": 404,
        },
    )


@app.get("/")
def read_root():
    """Point d'entrée de l'API — retourne un message de bienvenue."""
    return {"message": "Bienvenue sur l'API Catalogue"}

app.include_router(articles.router)
