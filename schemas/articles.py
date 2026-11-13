from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ArticleResponse(BaseModel):
    id: int
    titre: str
    contenu: str
    publie: bool = False
    date_creation: datetime
    categorie: Optional[str] = None
    nb_vues: int = Field(default=0, ge=0)

class ArticleCreation(BaseModel):
    titre: str = Field(min_length=3, max_length=200)
    contenu: str = Field(min_length=10)
    categorie: Optional[str] = None

# Modèle pour la MODIFICATION partielle (entrée) — tous les champs optionnels
class ArticleMiseAJour(BaseModel):
    titre: Optional[str] = Field(default=None, min_length=3, max_length=200)
    contenu: Optional[str] = Field(default=None, min_length=10)
    categorie: Optional[str] = None



