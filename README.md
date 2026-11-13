# Tutoriel FASTAPI / SQLALCHEMY

## installation de FastAPI avec uv

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


# création du fichier pyproject.toml
uv init --no-package


# ajout individuel des dépendances: au 1er import: uv créé le .venv !!!
uv add "fastapi[standard]"
# standard : FastAPI + Uvicorn
uv add fastapi --extra standard

# différencier les dépendances de production et de développement
uv add --dev "pytest"

# ex. de dépendance de production
uv add --prod "hypercorn[...]"

## bonne pratique: ne pas activer le .venv manuellement, laisser uv gérer l'environnement virtuel
uv run fastapi dev

```