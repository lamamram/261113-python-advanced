# Migration vers SQLAlchemy Async avec FastAPI

## pourquoi le faire ?

* fastapi gère des requêtes exécutées dans des threads.
si une requête effectue des opérations d'entrée/sortie (i/o) bloquantes, ex: appels à une base de données

* en utilisant les outils asynchrones et leurs coroutines, les opérations i/o peuvent être effectuées de manière non bloquante,
permettant à fastapi de gérer plus de requêtes en parallèle dans le même thread.

* Une coroutine python est une fonction définie avec **async def** qui, lorsqu'elle est exécutée par une **boucle d'événement**, peut se suspendre (avec **await**) pour céder le contrôle, puis être reprise plus tard.

## 📋 Vue d'ensemble

Ce document décrit les étapes pour migrer l'application FastAPI actuelle de SQLAlchemy **synchrone** vers **asynchrone**.

---

## 🔧 1. Installation des dépendances

```bash
# Installer les drivers async
pip install asyncpg  # Pour PostgreSQL
# OU
pip install aiomysql  # Pour MySQL
# OU  
pip install aiosqlite  # Pour SQLite

# SQLAlchemy async est déjà inclus dans sqlalchemy>=1.4
```

---

## 🗄️ 2. Modifier `database.py` - Engine et Session async

### Avant (Synchrone) :
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DB_URI = "sqlite:///persons.db"

engine = create_engine(
    DB_URI,
    connect_args={"check_same_thread": False},
    echo=True
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Après (Asynchrone) :
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

# ATTENTION: URL change - aiosqlite:// au lieu de sqlite://
DB_URI = "sqlite+aiosqlite:///persons.db"
# Pour PostgreSQL: "postgresql+asyncpg://user:pass@localhost/dbname"

async_engine = create_async_engine(
    DB_URI,
    echo=True,
    # pool settings si nécessaire
    # pool_size=20,
    # max_overflow=0
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

---

### Stratégie avec SQLAlchemy + PostgreSQL asynchrone

1. installer les outils : `pip install asyncpg`

2. `db.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# ...
DB_URI = "postgresql+asyncpg://Url"
# ...
async_engine = create_async_engine(
    DB_URI,
    # echo=True
)
# ...
AsyncSessionLocal = async_sessionmaker(autoflush=True, autocommit=False,class_=AsyncSession, bind=async_engine)
# ...
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    # asyn with remplace try / finally car la session est terminée en sortant du contexte
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 🏗️ 3. Modifier `models.py` - Pas de changement !

**Bonne nouvelle** : Les modèles SQLAlchemy 2.0 déclaratifs fonctionnent **tels quels** avec async.

```python
# ✅ Aucune modification nécessaire dans models.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    # ... reste identique
```

---

## 🔄 4. Modifier les routes - Ajouter async/await partout

### Avant (Synchrone) :
```python
from sqlalchemy.orm import Session
from ..orm.database import get_db

@user_router.get("/{user_id}")
def fetch_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserModel).where(UserModel.id == user_id))
    user = user.scalar()
    if not user:
        raise HTTPException(status_code=404)
    return user.to_dict()
```

### Après (Asynchrone) :
```python
from sqlalchemy.ext.asyncio import AsyncSession
from ..orm.database import get_async_db

@user_router.get("/{user_id}")
async def fetch_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404)
    return user.to_dict()
```

### Changements clés :
1. `def` → `async def`
2. `Session` → `AsyncSession`
3. `get_db` → `get_async_db`
4. `db.execute()` → `await db.execute()`
5. `db.commit()` → `await db.commit()`
6. `db.add()` → reste identique (pas async)
7. `db.refresh()` → `await db.refresh()`

---

## 📝 5. Exemples de requêtes courantes

### SELECT
```python
# Synchrone
users = db.execute(select(UserModel).limit(10)).scalars().all()

# Asynchrone
result = await db.execute(select(UserModel).limit(10))
users = result.scalars().all()
```

### INSERT
```python
# Synchrone
new_user = UserModel(username="alice", password="hash")
db.add(new_user)
db.commit()
db.refresh(new_user)

# Asynchrone
new_user = UserModel(username="alice", password="hash")
db.add(new_user)  # ✅ add() n'est pas async
await db.commit()
await db.refresh(new_user)
```

### UPDATE
```python
# Synchrone
user.username = "new_name"
db.commit()

# Asynchrone
user.username = "new_name"
await db.commit()
```

### DELETE
```python
# Synchrone
db.delete(user)
db.commit()

# Asynchrone
await db.delete(user)
await db.commit()
```

---

## 🔐 6. Modifier `auth.py` et routes d'authentification

### Exemple route login :
```python
from sqlalchemy.ext.asyncio import AsyncSession

@auth_router.post("/login")
async def login(
    credentials: LoginCredentials,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(UserModel).where(UserModel.username == credentials.username)
    )
    user = result.scalar()
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
```

---

## 🧪 7. Créer/mettre à jour les tables (init_db.py)

### Synchrone :
```python
from models import Base
from database import engine

Base.metadata.create_all(bind=engine)
```

### Asynchrone :
```python
import asyncio
from models import Base
from database import async_engine

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
```

---

## ⚠️ 8. Pièges courants

### ❌ Oublier await
```python
# ERREUR
user = db.execute(select(UserModel))  # Retourne un coroutine object

# CORRECT
result = await db.execute(select(UserModel))
user = result.scalar()
```

### ❌ Mélanger sync et async
```python
# ERREUR - utiliser Session avec async
async def route(db: Session = Depends(get_db)):
    await db.execute(...)  # TypeError

# CORRECT
async def route(db: AsyncSession = Depends(get_async_db)):
    await db.execute(...)
```

### ❌ Oublier async def
```python
# ERREUR
def route(db: AsyncSession = Depends(get_async_db)):
    await db.execute(...)  # SyntaxError: await outside async function

# CORRECT
async def route(db: AsyncSession = Depends(get_async_db)):
    await db.execute(...)
```

---

## 📦 9. Fichiers à modifier - Checklist

- [ ] `database.py` : engine → async_engine, Session → AsyncSession
- [ ] Toutes les routes dans `routers/user_router.py` : def → async def, await
- [ ] `routers/auth_router.py` : def → async def, await
- [ ] `init_db.py` : asyncio.run() avec async/await
- [ ] Tous les `Depends(get_db)` → `Depends(get_async_db)`
- [ ] Tous les `db.execute()` → `await db.execute()`
- [ ] Tous les `db.commit()` → `await db.commit()`
- [ ] Tous les `db.refresh()` → `await db.refresh()`

---

## 🎯 10. Avantages et inconvénients

### ✅ Avantages :
- **Meilleure concurrence** : gère plus de requêtes simultanées
- **Moins de ressources** : un seul thread pour des milliers de connexions
- **Performance I/O** : idéal pour appels DB + APIs externes multiples

### ❌ Inconvénients :
- **Complexité** : tout le code doit être async (chaîne complète)
- **Debugging** : stack traces plus complexes
- **Compatibilité** : toutes les librairies doivent supporter async
- **Migration** : nécessite de tout réécrire

---

## 💡 Recommandation

**Pour cette application** :
- Si < 100 utilisateurs simultanés → **garder synchrone** (plus simple)
- Si > 1000 utilisateurs simultanés → **migrer vers async**
- Si appels externes multiples (APIs, microservices) → **async recommandé**

FastAPI gère déjà bien le sync avec son threadpool automatique !

---

## 📚 Ressources

- [SQLAlchemy Async docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [asyncpg](https://github.com/MagicStack/asyncpg)
