# ------------------- inejections de configuration avec @dataclass et load_dotenv --------------
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field

load_dotenv()

@dataclass(
    frozen=True,
    kw_only=True
)
class Settings:
    base_url: str = ""
    token: str | None = field(default=None, repr=False)
    timeout: tuple[float, float] = (3.05, 10.0)
    allow_redirects: bool = False

    @classmethod
    def form_env(cls):
        """méthode de classe à utilier directement avec Settings.from_env(...)"""
        return cls(
            base_url=os.getenv('GOREST_BASE_URL'),
            token=os.getenv('GOREST_TOKEN') or None
        )