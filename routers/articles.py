# routers/articles.py
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import Optional, List
from schemas.articles import ArticleResponse, ArticleCreation, ArticleMiseAJour
from datetime import datetime
from exceptions import ArticleNonTrouveException
from auth import UtilisateurDansToken, get_current_user

# ------------------------------------> tags qui servent à tout
router = APIRouter(prefix="/articles", tags=["Articles"])

# Base de données fictive en mémoire
articles_db: list[dict] = [
    {"id": 1, "titre": "Intro FastAPI", "contenu": "...", "publie": True,
     "date_creation": "2024-01-15T10:00:00", "nb_vues": 150, "categorie": "python",
     "mot_de_passe_interne": "ne_pas_exposer", "slug": "intro-fastapi"},
    {"id": 2, "titre": "Avancé FastAPI", "contenu": "...", "publie": False, 
     "date_creation": "2024-01-20T15:00:00", "nb_vues": 75, "categorie": "python",
     "mot_de_passe_interne": "ne_pas_exposer", "slug": "avance-fastapi"},
    {"id": 3, "titre": "FastAPI et SQLAlchemy", "contenu": "...", "publie": True,
     "date_creation": "2024-02-01T12:00:00", "nb_vues": 200, "categorie": "orm",
     "mot_de_passe_interne": "ne_pas_exposer", "slug": "fastapi-et-sqlalchemy"}
]

# --- Base de données simulée ---

_compteur_id = 0
articles_db: dict[int, dict] = {}

def _nouvel_id() -> int:
    global _compteur_id
    _compteur_id += 1
    return _compteur_id


#  /articles/
@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    page: int = Query(default=1, ge=1, description="Numéro de page (commence à 1)"),
    taille: int = 10,
    # ------->   : str | None
    categorie: Optional[str] = None,
):
    """Liste les articles avec pagination et filtre optionnel par catégorie."""
    if categorie:
        articles = [a for a in articles_db if a.get("categorie") == categorie]
    debut = (page - 1) * taille
    return articles_db [debut : debut + taille] if not categorie else  articles[debut : debut + taille]

# /articles/{article_id}
# --------------------------> Schéma == Contrat != model au sens MVC !
# -----------------------------------------> contrôle la réponse FastAPI
@router.get("/{article_id}", response_model=ArticleResponse)
# --------------------------------> contraintes de paramètre de chemin + documentation openapi
def get_article(article_id: int = Path(gt=0, description="Identifiant entier positif de l'article")):
    if article_id not in articles_db:
        # redirige la réponse vers le gestionnaire d'exception ad hoc cf main.py
        raise ArticleNonTrouveException(article_id=article_id)
    return articles_db[article_id - 1]

# ----------------------------------------------> status
@router.post(
    "/",
    response_model=ArticleResponse,
    status_code=201,
    summary="Créer un article",
    description="""
Crée un nouvel article dans la base de données.

L'identifiant est généré automatiquement côté serveur.
La date de création est définie au moment de la requête.
""",
    response_description="L'article créé avec son identifiant et sa date de création",
    responses={
        409: {"description": "Un article avec ce titre existe déjà"},
    },
)
def create_article(article: ArticleCreation):
    """Crée un nouvel article et retourne l'article créé avec son ID."""
    nouvel_id = _nouvel_id()
    nouvel_article = {
        "id": nouvel_id,
        # injecter les champs de la requête POST dûment validés par le schéma Pydantic en paramètre du handler
        **article.model_dump(),
        "publie": False,
        "date_creation": datetime.now()
,
    }
    articles_db[nouvel_id] = nouvel_article
    return nouvel_article

# curl -X POST "http://127.0.0.1:8000/articles/" -H "Content-Type: application/json" -d '{"titre": "Nouvel article", "contenu": "Contenu de l article", "categorie": "python"}'

@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, article: ArticleMiseAJour):
    """Met à jour partiellement l'article (PATCH = modification partielle)."""
    if article_id not in articles_db:
        raise HTTPException(status_code=404, detail=f"Article {article_id} introuvable")
    # ------------------------------> élaguer les champs inutilisés (None) avant la mise à jour
    mises_a_jour = article.model_dump(exclude_none=True)  # Ignore les champs None
    articles_db[article_id].update(mises_a_jour)
    return articles_db[article_id]


@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: int = Path(gt=0),
    # une dépendance créé par l'utilisateur mais intégrée à FastAPI via Depends()
    user: UtilisateurDansToken = Depends(get_current_user)
):
    """Supprime l'article ou retourne 404."""
    print(user.username)
    articles = list(filter(lambda d: d["id"] == article_id, articles_db))
    if not articles:
        raise HTTPException(status_code=404, detail=f"Article {article_id} introuvable")
    for i in range(len(articles_db)):
        if articles[0]["id"] == articles_db[i]["id"]:
            del articles_db[i]
            break

# curl -X DELETE "http://127.0.0.1:8000/articles/1" -H "Authorization: Bearer <token>"