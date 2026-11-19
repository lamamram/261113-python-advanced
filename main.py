# main.py
from fastapi import FastAPI
from middlewares import install_middlewares
# -- optimisation de fastapi pour importer un module depuis un package
from routers import articles, auth
from exceptions import install_handlers
from fastapi.responses import JSONResponse


app = FastAPI(
    title="API Catalogue",
    description="Premier projet FastAPI — formation Dawan",
    version="0.1.0",
    openapi_tags=[
        {"name": "Articles", "description": "Gestion des articles du catalogue"},
        {"name": "Auteurs", "description": "Gestion des profils auteurs"},
        {"name": "Santé", "description": "Endpoints de monitoring"},
    ]
)


@app.get("/")
def read_root():
    """Point d'entrée de l'API — retourne un message de bienvenue."""
    return {"message": "Bienvenue sur l'API Catalogue"}

app.include_router(articles.router)
app.include_router(auth.router)
install_handlers(app)
install_middlewares(app)
