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
