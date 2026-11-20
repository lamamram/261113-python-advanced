from pydantic import BaseModel as BaseSchema, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import re

class ArticleFormatMixin(BaseSchema):
    """
    Mixin pour formater les tags en minuscules et sans espaces superflus.

    check_fields=False permet de valider même si le champ n'est pas défini dans le modèle.
    """
    @field_validator(
            "tags", 
            check_fields=False, 
            # mode="before"
    )
    @classmethod
    def tags_en_minuscules(cls, v: list[str]) -> list[str]:
        """ transformation impossible avec un champs composite depuis Field !!! """
        return [tag.nom.lower().strip() for tag in v]

class ArticleResponse(ArticleFormatMixin):
    id: int
    titre: str
    # slug: Optional[str] = Field(default=None, pattern="^[a-z0-9-]+$", example="mon-article")
    contenu: str
    publie: bool = False
    date_creation: datetime
    # categorie: Optional[str] = None
    nb_vues: int = Field(default=0, ge=0)
    # liste de tags possiblemement vide par défaut
    tags: List["TagSchema"] = Field(default_factory=list)



class ArticleCreation(ArticleFormatMixin):
    titre: str = Field(min_length=3, max_length=200)
    # slug: Optional[str] = None
    # ----------------------------------> validation sur le champs via un attribut simple
    contenu: str = Field(min_length=10, pattern="^content:.*")
    # categorie: Optional[str] = None
    tags: List[TagSchema] = Field(default_factory=list)
    auteur_id: int = Field(default=1)


    # @model_validator(mode="after")
    # def generer_slug_si_absent(self) -> "ArticleCreation":
    #     """Génère automatiquement un slug depuis le titre si non fourni.
    #        besoin de l'objet schéma pour transformation multi champs"""
    #     if self.slug is None:
    #         self.slug = re.sub(r"[^a-z0-9]+", "-", self.titre.lower()).strip("-")
    #     return self

# Modèle pour la MODIFICATION partielle (entrée) — tous les champs optionnels
class ArticleUpdate(ArticleFormatMixin):
    titre: Optional[str] = Field(default=None, min_length=3, max_length=200)
    contenu: Optional[str] = Field(default=None, min_length=10)
    # categorie: Optional[str] = None
    tags: Optional[List[TagSchema]] = None

class TagSchema(BaseSchema):
    id: int
    nom: str



