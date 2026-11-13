from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

from dotenv import load_dotenv
import os

from pydantic import BaseModel

# charge le fichier .env.*
load_dotenv()

### configuration d'un jeton JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 30

# Hachage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Schéma OAuth2 Password — l'URL du endpoint de login

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

UTILISATEURS_DB = {
    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash("secret")
    }
}

# # --------------------- schémas --------------------

class TokenReponse(BaseModel):
    access_token: str
    token_type: str

class UtilisateurDansToken(BaseModel):
    username: str

# # ---------------------- helpers -----------

#url-encoded que demande OAuth2PasswordRequestForm
# curl -X POST "http://127.0.0.1:8000/auth/token" -F "username=alice" -F "password=secret"

def creer_jeton(data: dict, expire_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now() + (expire_delta or timedelta(minutes=EXPIRE_MINUTES))
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# # ------------- gestion de mot de passe fake ------------------

def verifier_mot_de_passe(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def authentifier_utilisateur(username: str, password: str) -> Optional[dict]:
    user = UTILISATEURS_DB.get(username)
    if not user or not verifier_mot_de_passe(password, user["hashed_password"]):
        return None
    return user


# ------------------------ dépéndance custom pour récupérer l'utilisateur courant à partir du token --------------

# --- Dépendances d'authentification ---

# --- la dépendance oauth2_scheme prelèe le token dans l'en-tête Authorization: "Bearer <token>"
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UtilisateurDansToken:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # décoder le token JWT pour extraire le username (sub)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    #le username du token existe ? user ou None
    user = UTILISATEURS_DB.get(username)
    if user is None:
        raise credentials_exception
    return UtilisateurDansToken(**user)