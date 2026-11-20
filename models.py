from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey, Table, CHAR, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from pwdlib import PasswordHash
from typing import List
from datetime import datetime

password_hash = PasswordHash.recommended()

#### Many-to-Many relationship between Article and Tag
# Table d'association, pas un modèle, définie avec Table() car elle n'a pas de modèle ORM propre
articles_tags = Table(
    "articles_tags",
    Base.metadata,
    ## on a une clé primaire composite sur les deux colonnes pour garantir l'unicité de chaque association article-tag
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

#### MODELES (tables) 

class Utilisateur(Base):
    """
    Modèle représentant un utilisateur.
    Chaque instance de cette classe correspond à une ligne dans la table 'utilisateurs'.
    """
    __tablename__ = "utilisateurs"  # Nom de la table dans la base de données

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Clé primaire auto-incrémentée
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # Nom d'utilisateur unique et obligatoire
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)  # Mot de passe haché obligatoire
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Indique si l'utilisateur est actif, par défaut True
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Indique si l'utilisateur est administrateur, par défaut False
    # Date de création, par défaut la date actuelle calculée par la base de données 
    # func permet d'utiliser les fonctions de la bdd ici NOW()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    ## relations
    articles: Mapped[List["Article"]] = relationship(
        back_populates="auteur",
        cascade="all, delete-orphan")  # Relation avec les articles écrits par l'utilisateur

    profil: Mapped["ProfilUtilisateur"] = relationship(
        back_populates="utilisateur",
        uselist=False,      # uselist=False → attribut unique, pas une liste
    )
    def __str__(self):
        """
        Représentation en chaîne de caractères de l'objet Utilisateur.
        Utile pour le débogage et la journalisation.
        """
        return f"Utilisateur(id={self.id}, username='{self.username}', email='{self.email}', active={self.active}, is_admin={self.is_admin}, created_at={self.created_at})"
    
    def hash_password(self):
        """
        Hache le mot de passe en clair et le stocke dans l'attribut hashed_password.
        utilisant password_hash.hash() pour le hachage sécurisé.
        """
        self.hashed_password = password_hash.hash(self.hashed_password)

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    publie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    auteur_id: Mapped[int] = mapped_column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    ## relations: ce ne sont pas des colonnes de la table, on les utilise en python
    # sur un objet article = Article(), on a article.auteur
    # grâce à back_populates, on peut faire l'inverse: sur un objet utilisateur = Utilisateur(), on a utilisateur.articles
    auteur: Mapped["Utilisateur"] = relationship(back_populates="articles", lazy="joined")  # lazy="joined" permet de charger l'auteur en même temps que l'article (jointure SQL)
    tags: Mapped[List["Tag"]] = relationship(
        secondary=articles_tags, back_populates="articles", lazy="selectin"
    )


    def __str__(self):
        return f"Article(id={self.id}, titre='{self.titre}', publie={self.publie}, date_creation={self.date_creation}, auteur_id={self.auteur_id})"

class ProfilUtilisateur(Base):
    __tablename__ = "profils_utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("utilisateurs.id"),
        unique=True,       # unique=True garantit le 1-à-1
        nullable=False,
    )
    bio: Mapped[str] = mapped_column(Text, default="")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")

    utilisateur: Mapped["Utilisateur"] = relationship(
        "Utilisateur", back_populates="profil"
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # relations
    articles: Mapped[list["Article"]] = relationship(
        secondary=articles_tags, back_populates="tags"
    )