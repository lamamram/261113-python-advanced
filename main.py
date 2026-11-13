# main.py
from fastapi import FastAPI

app = FastAPI(
    title="API Catalogue",
    description="Premier projet FastAPI — formation Dawan",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Point d'entrée de l'API — retourne un message de bienvenue."""
    return {"message": "Bienvenue sur l'API Catalogue"}


@app.get("/articles/{article_id}")
def get_article(article_id: int):
    """Retourne un article fictif identifié par son ID entier."""
    return {"id": article_id, "titre": f"Article numéro {article_id}"}
