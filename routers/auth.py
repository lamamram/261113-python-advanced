from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import creer_jeton, authentifier_utilisateur, TokenReponse


router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/token", response_model=TokenReponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    le service d'authentification OAuth2 vient d'un tiers fournisseur
    ici on authentifie l'utilisateur avec notre propre base de données donc Depends()
    Depends: surcouche crée par FastAPI pour intégrer les dépendances tierces ou internes
       1. au sein du cycle de vie d'une requête FastAPI
       2. être liée à une action de validations
       3. en synchrone utilisse une pool de threads (I/O)
       4. et fonctionne avec async et await pour les opérations asynchrones
    """
    user = authentifier_utilisateur(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = creer_jeton({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}