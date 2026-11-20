from sqlalchemy import create_engine, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, Column, func
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship
# pip install python-dotenv
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List, Generator

load_dotenv()  # charge les variables d'environnement depuis le fichier .env

pg_user = os.getenv("PG_USER", "root")
pg_pass = os.getenv("PG_PASS", "")
pg_host = os.getenv("PG_HOST", "localhost")
pg_port = os.getenv("PG_PORT", "5432")
pg_db = os.getenv("PG_DB", "default")

######################## CONFIGURATION d'un sessions SQLAlchemy pour PostgreSQL ########################

# chaine de connexion (connection string) pour 
DATABASE_URL = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
engine = create_engine(
    DATABASE_URL,
    pool_size=15,  # nombre maximum de connexions persistentes dispos dans le pool pour les utilisateurs
    max_overflow=5,  # nombre maximum de connexions supplémentaires au-delà du pool_size en cas de pic
    # mode debug: affiche les requêtes SQL générées par SQLAlchemy dans la console
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,# les transactions ne sont pas validées automatiquement, il faut appeler session.commit() pour valider
    autoflush=False, 
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    1. Fournit une session de base de données SQLAlchemy pour chaque requête FastAPI.
    en utilisant le mécanisme Depends(get_db) pour rendre la session dispo dans les gestionnaires fastAPI
    2. sa forme de générateur (yield) permet de temporiser l'execution après le yield 
    et de de s'assurer que la session est toujours fermée après utilisation, même en cas d'exception.
    """
    db = SessionLocal()
    try:
        yield db          # Fournit la session
    finally:
        db.close()        # Toujours fermer même en cas d'exception

####################### MODELISATION DES MODELES (tables) avec SQLAlchemy #######################

class Base(DeclarativeBase):
    """
    Classe de base pour les modèles SQLAlchemy.
    Tous les modèles (tables) doivent hériter de cette classe.
    Base permet également de créer des méthodes et des attributs communs à tous les modèles si nécessaire.
    """
    pass
