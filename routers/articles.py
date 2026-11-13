# routers/articles.py
from fastapi import APIRouter, Path, Query
from typing import Optional, List
from schemas.articles import ArticleResponse

# ------------------------------------> tags qui servent à tout
router = APIRouter(prefix="/articles", tags=["Articles"])

# Base de données fictive en mémoire
articles_db: list[dict] = [
    {"id": 1, "titre": "Intro FastAPI", "contenu": "...", "publie": True,
     "date_creation": "2024-01-15T10:00:00", "nb_vues": 150, "categorie": "python",
     "mot_de_passe_interne": "ne_pas_exposer"},
    {"id": 2, "titre": "Avancé FastAPI", "contenu": "...", "publie": False, 
     "date_creation": "2024-01-20T15:00:00", "nb_vues": 75, "categorie": "python",
     "mot_de_passe_interne": "ne_pas_exposer"},
    {"id": 3, "titre": "FastAPI et SQLAlchemy", "contenu": "...", "publie": True,
     "date_creation": "2024-02-01T12:00:00", "nb_vues": 200, "categorie": "orm",
     "mot_de_passe_interne": "ne_pas_exposer"}

]

#  /articles/
@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    page: int = Query(default=1, ge=1, description="Numéro de page (commence à 1)"),
    taille: int = 10,
    # ------->   : str | None
    categorie: Optional[str] = None,
):
    """
    GET /articles → page=1, taille=10

    GET /articles?page=2&taille=5 → page=2, taille=5
    
    GET /articles?categorie=python → filtre par catégorie
    """
    return {
        "page": page,
        "taille": taille,
        "categorie": categorie,
        "articles": [],
    }

# /articles/{article_id}
# --------------------------> Schéma == Contrat != model au sens MVC !
# -----------------------------------------> contrôle la réponse FastAPI
@router.get("/{article_id}", response_model=ArticleResponse)
# --------------------------------> contraintes de paramètre de chemin + documentation openapi
def get_article(article_id: int = Path(gt=0, description="Identifiant entier positif de l'article")):
    return articles_db[article_id - 1]
