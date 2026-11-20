# routers/articles.py
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import Optional, List
from schemas.articles import ArticleResponse, ArticleCreation, ArticleUpdate
from datetime import datetime
from exceptions import ArticleNotFoundException
# ------------------> il y a déjà une classe Session dans Fastapi
from auth import UserInToken, get_current_user

################ ORM #############
from database import Session as DbSession, get_db
from async_database import AsyncSession as AsyncDbSession, get_async_db
from models import Article
from sqlalchemy import select, update

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

_compteur_id = len(articles_db)

def _nouvel_id() -> int:
    global _compteur_id
    _compteur_id += 1
    return _compteur_id

def _get_by_id(article_id: int) -> dict:
    article = next((a for a in articles_db if a["id"] == article_id), None)
    return article

def _get_by_categorie(categorie: str) -> list[dict]:
    return [a for a in articles_db if a["categorie"] == categorie]

# ------------------------------------------------------------------------------------


#  /articles/
@router.get("/async", response_model=List[ArticleResponse])
async def list_articles(
    page: int = Query(default=1, ge=1, description="Numéro de page (commence à 1)"),
    taille: int = 10,
    # ------->   : str | None
    publie: Optional[str] = None,
    db: AsyncDbSession = Depends(get_async_db)
):
    """Liste les articles avec pagination et filtre optionnel par catégorie."""   
    debut = (page - 1) * taille
    stmt = select(Article)
    if publie:
        stmt = stmt.where(Article.publie == True)

    # uniquement execute qui retourne ici une coroutine ==> Awaitable !!
    articles = await db.execute(stmt)
    articles = articles.scalars().all()

    return articles

#  /articles/
@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    page: int = Query(default=1, ge=1, description="Numéro de page (commence à 1)"),
    taille: int = 10,
    # ------->   : str | None
    publie: Optional[str] = None,
    db: DbSession = Depends(get_db)
):
    """Liste les articles avec pagination et filtre optionnel par catégorie."""   
    debut = (page - 1) * taille
    stmt = select(Article)
    if publie:
        stmt = stmt.where(Article.publie == True)
    # ------------------->Result-> Results[Article] -> List[Articles] 
    # ---------- req réutilisable après ---
    # ------------------------------------ données ------
    # articles = db.execute(stmt).scalars().all()

    # les données directement : synchrone
    articles = db.scalars(
        stmt
        .limit(debut + taille)
        .offset(debut)
    ).all()
    return articles

# /articles/{article_id}
# --------------------------> Schéma == Contrat != model au sens MVC !
# -----------------------------------------> contrôle la réponse FastAPI
@router.get("/{article_id}", response_model=ArticleResponse)
# --------------------------------> contraintes de paramètre de chemin + documentation openapi
def get_article(
    article_id: int = Path(gt=0, description="Identifiant entier positif de l'article"),
    db: DbSession = Depends(get_db)
):
    #------------> vérifie si l'objet est dans le cache mémoire (identity map) avant de demander à la base
    article = db.get(Article, article_id)
    if not article:
        # redirige la réponse vers le gestionnaire d'exception ad hoc cf exceptions.py
        raise ArticleNotFoundException(article_id=article_id)
    return article

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
def create_article(article: ArticleCreation, db: DbSession = Depends(get_db)):
    """Crée un nouvel article et retourne l'article créé avec son ID."""

    nouvel_article = Article(**article.model_dump())
    db.add(nouvel_article) # marquer en insertion: calcule les ids et defaults mais ne les ajoute pas à l'objet !!!
    
    # db.flush() # ici les ids sont accessibles dans l'objet et dans la session pour continuer le code métier comme si on avait commité !!!    
    
    db.commit()
    return nouvel_article

# curl -X POST "http://127.0.0.1:8000/v1/articles/" -H "Content-Type: application/json" -d '{"titre": "Nouvel article", "contenu": "content:Contenu de l article", "publie": false}'

@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, article_update: ArticleUpdate, db: DbSession = Depends(get_db)):
    """Met à jour partiellement l'article (PATCH = modification partielle)."""
    
    this_article = db.get(Article, article_id)
    if not this_article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} introuvable")
    # ------------------------------> élaguer les champs inutilisés (None) avant la mise à jour
    updates = article_update.model_dump(exclude_none=True)  # Ignore les champs None
    
    # version orm : pour un objet + simple
    # for field, value in updates.items():
    #     setattr(this_article, field, value)
    # db.commit()
   
    # version core: pour update massifs !!
    # --------------------> WHERE du pauvre, -----> SET key=value
    stmt = update(Article).filter_by(id=article_id).values(updates)
    db.execute(stmt)
    db.commit()
    db.refresh(this_article) # annule les modifications d'objets python en écrasant la version de la db
    # flush : confirmer les changement côté python

    return this_article


@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: int = Path(gt=0),
    # une dépendance créé par l'utilisateur mais intégrée à FastAPI via Depends()
    user: UserInToken = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    """Supprime l'article ou retourne 404."""
    this_article = db.get(Article, article_id)
    
    if not this_article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} introuvable")
    db.delete(this_article) # marque comme suppression
    db.commit()

# curl -X DELETE "http://127.0.0.1:8000/v1/articles/1" -H "Authorization: Bearer <token>"