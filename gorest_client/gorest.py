from .config import Settings
from typing import Any
from urllib.parse import quote
from collections.abc import Iterator
import requests
from .exceptions import *
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

class GoRestClient:
    """
    classe qui rélise une couche d'indirection pour masquer l'utilisation de requests/urllib3 ... et HTTP
    c'est un gestionnaire de contexte qui ouvre et ferme des sessions requests
    """
    def __init__(
            self, 
            settings: Settings | None = None, 
            headers: dict[str, Any]={}
        ):
        self.settings = settings or Settings.form_env()
        # ------------------------------------> gérer le / final s'il existe !
        self.base_url = self.settings.base_url.rstrip("/")

        # entêtes par défauts
        self.headers = { 
            **headers, 
            "Accept": "application/json",
            "User-Agent": "gorest-client/1.0"
        }

        # config retry
        self.retry = Retry(
            total=3,
            backoff_factor=0.5,
            backoff_jitter=0.5,
            status_forcelist=(429, 404, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )

    ### trnasforme une classe custom en gestionnaire de contexte

    def __enter__(self):
        """
        cette méthode doit retourner un objet qui contient la session à droite du "as"
        """
        self.session = requests.Session()
        self.session.headers = self.headers
        if self.settings.token:
            self.session.auth = BearerAuth(self.settings.token)
        self.session.mount("https://", HTTPAdapter(max_retries=self.retry))
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

    ### socle ##################################

    def __call(self, method: str, path: str, **options: Any):
        """
        **options couvre: params, data, cookies, files
        """
        options.setdefault("timeout", self.settings.timeout)
        options.setdefault("allow_redirects", self.settings.allow_redirects)
        url = f"{self.base_url}/{path.lstrip('/')}"

        # crée une request.Request + prepare + send
        r = self.session.request(method=method, url=url, **options)

        # r.ok ==> [ 200 - 400 [ mais avec allow_redirects : 3xx -> 4xx
        if r.ok:
            if "application/json" in r.headers["content-type"]:
                return r
            raise ApiError(r.status_code, {"detail": "réponse non JSON !!!"})
        raise self._error(r)

    ### helper #############################
    @staticmethod
    def _path(resource: str, _id: str) -> str:
        return f"{resource}/{quote(_id, safe='')}"

    @staticmethod
    def _error(r: requests.Response):
        # -------------------> erreur connue / inconnue
        return PAR_STATUT.get(r.status_code, ApiError)(r.status_code, r.json())

    ### interface publique ###################################

    def list(
            self, resource: str, 
            params: dict[str, Any] = {},
            taille: int = 5
        ) -> Iterator[dict[str, Any]]:
            params = {**params, "page[size]": taille}
            while True:
                # -------------------------------> appel nommé k=v => mis auto. dans **options
                obj = self.__call("GET", resource, params=params).json()
                yield from obj["data"]
                if not obj["meta"]["has_more"]:
                    return
                params["page[after]"] = obj["meta"]["next_cursor"]

    def get(self, resource: str, _id: str) -> dict[str, Any]:
        r = self.__call("GET", self._path(resource, _id))
        # ---------------> je peux enregistre l'etag pour garantir la valeur courante de l'objet
        return r.json(), r.headers["ETag"]

    def post(self, resource: str, json: dict[str, Any]) -> dict[str, Any]:
        return self.__call("POST", resource, json=json).json()

    def patch(
            self, 
            resource: str, 
            _id: str, 
            updates: dict[str, Any],
            etag: str = ""
        ) -> dict[str, Any]:
            ## fonctionne si le etag a été modifié entre temps
            headers = {"If-Match": etag} if etag else {}
            return self.__call("PATCH", self._path(resource, _id), json=updates, headers=headers).json()






    