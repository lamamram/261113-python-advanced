from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import re

class ArticleResponse(BaseModel):
    id: int
    titre: str
    slug: Optional[str] = None
    contenu: str
    publie: bool = False
    date_creation: datetime
    categorie: Optional[str] = None
    nb_vues: int = Field(default=0, ge=0)
    # liste de tags possiblemement vide par défaut
    tags: List[TagSchema] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def tags_en_minuscules(cls, v: list[str]) -> list[str]:
        """ transformation impossible avec un champs composite depuis Field !!! """
        return [tag.nom.lower().strip() for tag in v]



class ArticleCreation(BaseModel):
    titre: str = Field(min_length=3, max_length=200)
    slug: Optional[str] = None
    # ----------------------------------> validation sur le champs via un attribut simple
    contenu: str = Field(min_length=10, pattern="^content:.*")
    categorie: Optional[str] = None
    tags: List[TagSchema] = Field(default_factory=list)


    @model_validator(mode="after")
    def generer_slug_si_absent(self) -> "ArticleCreation":
        """Génère automatiquement un slug depuis le titre si non fourni.
           besoin de l'objet schéma pour transformation multi champs"""
        if self.slug is None:
            self.slug = re.sub(r"[^a-z0-9]+", "-", self.titre.lower()).strip("-")
        return self

# Modèle pour la MODIFICATION partielle (entrée) — tous les champs optionnels
class ArticleMiseAJour(BaseModel):
    titre: Optional[str] = Field(default=None, min_length=3, max_length=200)
    contenu: Optional[str] = Field(default=None, min_length=10)
    categorie: Optional[str] = None

class TagSchema(BaseModel):
    id: int
    nom: str



