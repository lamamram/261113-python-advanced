# main.py
from fastapi import FastAPI
# -- optimisation de fastapi pour importer un module depuis un package
from routers import articles


app = FastAPI(
    title="API Catalogue",
    description="Premier projet FastAPI — formation Dawan",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Point d'entrée de l'API — retourne un message de bienvenue."""
    return {"message": "Bienvenue sur l'API Catalogue"}

app.include_router(articles.router)
