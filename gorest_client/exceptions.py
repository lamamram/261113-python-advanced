class ApiError(Exception):
    """Réponse d'erreur du service (corps Problem Details si présent)."""

    def __init__(self, status: int, problem: dict | None = None):
        self.status = status
        self.problem = problem or {}
        self.code = self.problem.get("code")
        self.errors = self.problem.get("errors", [])
        self.request_id = self.problem.get("request_id")
        detail = self.problem.get("detail") or self.problem.get("title") or "erreur HTTP"
        super().__init__(f"{status} {self.code or ''} {detail}".strip())


class AuthError(ApiError): ...          # 401, 403
class NotFound(ApiError): ...           # 404
class ValidationFailed(ApiError): ...   # 422
class RateLimited(ApiError): ...        # 429

PAR_STATUT: dict[int, type[ApiError]] = {
    401: AuthError, 403: AuthError, 404: NotFound,
    422: ValidationFailed, 429: RateLimited,
}