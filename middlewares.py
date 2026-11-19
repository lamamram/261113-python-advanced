from fastapi import FastAPI, Request
import time


def install_middlewares(app: FastAPI):
    @app.middleware("http")
    async def ajouter_duree_traitement(request: Request, call_next):
        ##### avant l'appel du gestionnaire, on mesure le temps de début
        debut = time.perf_counter()
        response = await call_next(request)
        ##### après l'appel du gestionnaire, on mesure le temps écoulé
        duree = time.perf_counter() - debut
        response.headers["X-Process-Time"] = f"{duree:.4f}s"
        return response