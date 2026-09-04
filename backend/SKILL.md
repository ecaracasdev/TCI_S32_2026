---
name: fastapi-async-nap
description: >
  Convenciones de arquitectura en capas para el proyecto FastAPI de Nico.
  Usar este skill en CUALQUIER tarea que involucre generar o modificar código
  en este proyecto: routers, services, db_models, DTOs, o cualquier decisión
  de estructura. Si el usuario pide crear un endpoint, un modelo, un servicio,
  una tabla, o cualquier pieza de este backend — este skill es obligatorio.
  También aplica cuando se discute organización de capas, naming, relaciones
  entre modelos, o patrones de servicio. No esperar a que el usuario diga
  "usa la skill": si el código es de este proyecto FastAPI, activar siempre.
---

# FastAPI Layered — Convenciones del Proyecto

## Stack

- **FastAPI** + **SQLAlchemy async** (`AsyncSession`, `create_async_engine`)
- **SQLite** en dev/local (`sqlite+aiosqlite:///`), **Postgres** en prod (`postgresql+asyncpg://`)
- Driver configurado via `.toml` — cambiar `DB_TYPE` y `DB_DRIVER` es suficiente para rotar de motor
- **Sin Docker en dev**. Todo corre local.

---

## Estructura de capas

```
proyecto/
├── app.py                  # Entry point, middlewares, routers, lifespan
├── config.py               # Modelos Pydantic de configuración
├── utils.py                # load_config, get_config, update_config
├── logs.py                 # load_logger, get_logger
├── db/
│   ├── database.py         # AsyncEngine, async_sessionmaker, get_db dependency
│   └── db_models/
│       ├── __init__.py     # Importa todos los modelos (necesario para create_all)
│       ├── base.py         # Base declarativa
│       └── <domain>.py     # Un archivo por aggregate root
├── models/                 # DTOs Pydantic para la API
│   └── <domain>.py
├── services/
│   ├── base.py             # BaseService[T] genérico async
│   ├── __init__.py         # Factories de Depends
│   └── <domain>_service.py
└── routers/
    ├── __init__.py         # Lista de routers exportados
    └── <domain>_router.py
```

---

## Naming

| Capa | Archivo | Clase |
|------|---------|-------|
| ORM model | `db/db_models/client.py` | `ClientDb` |
| DTO | `models/client.py` | `ClientDto`, `ClientCreateDto`, `ClientUpdateDto` |
| Service | `services/client_service.py` | `ClientService` |
| Router | `routers/client_router.py` | `router` |

Sufijos estrictos: `Db` para ORM, `Dto` para Pydantic, `Service` para services.

---

## Sesión y ciclo de vida

`BaseService` **no gestiona la sesión**. La recibe ya abierta, opera dentro de ella, nada más.  
El ciclo de vida (abrir → commit → rollback → cerrar) es responsabilidad exclusiva de `get_db()` en `database.py`.

```python
# database.py — no tocar este patrón
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_sessionmaker()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

El engine (`get_engine()`) y el sessionmaker (`get_sessionmaker()`) son lazy singletons legítimos: son stateless y viven toda la vida del proceso.

---

## ORM Models — Aggregate Root

**Un service por aggregate root, no por tabla.**  
Si una entidad nunca existe de forma independiente (ej: `Address` siempre pertenece a `Client`), no necesita service propio. Se accede via relationship desde el root.

```python
# db/db_models/client.py
from db.db_models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class ClientDb(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = relationship("AddressDb", back_populates="client", lazy="selectin", uselist=False)


class AddressDb(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("ClientDb", back_populates="address")
```

### `lazy="selectin"` — regla de uso

- **Siempre usar `lazy="selectin"`** en relationships que se consumen frecuentemente junto al padre.
- SQLAlchemy emite una segunda query eficiente al cargar el padre. El objeto relacionado ya está disponible sin segunda llamada manual.
- `lazy="joined"` solo si el JOIN es más barato que dos queries (tablas pequeñas, relación 1:1 siempre presente).
- **Nunca `lazy="select"` (default)** en modo async — genera `MissingGreenlet` error al acceder al atributo fuera de contexto async.

### Tablas pivot

- Si el pivot no tiene campos propios: no crear modelo ni service. Acceder via `back_populates` desde el root.
- Si el pivot tiene campos propios (fecha, estado, cantidad): crear `PivotDb` y manejar desde el service del aggregate root más relevante.

---

## DTOs (`models/<domain>.py`)

```python
from pydantic import BaseModel
from typing import Optional

class AddressDto(BaseModel):
    id: int
    street: str
    model_config = {"from_attributes": True}

class ClientDto(BaseModel):
    id: int
    name: str
    address: AddressDto | None = None  # nested — se serializa automáticamente
    model_config = {"from_attributes": True}

class ClientCreateDto(BaseModel):
    name: str

class ClientUpdateDto(BaseModel):
    name: Optional[str] = None
```

- `Dto` = lectura/respuesta. Siempre `model_config = {"from_attributes": True}`.
- `CreateDto` = payload de creación. Sin `id`.
- `UpdateDto` = patch parcial. Todos los campos `Optional`.
- DTOs anidados para relaciones que siempre se consumen juntas.
- No mezclar lógica de negocio en DTOs.

---

## Services (`services/<domain>_service.py`)

Heredan de `BaseService[T]`. El constructor recibe solo `session: AsyncSession`.  
Métodos adicionales solo para queries específicas del dominio.

```python
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_models.client import ClientDb
from .base import BaseService


class ClientService(BaseService[ClientDb]):
    """Handles business logic for clients (aggregate root: includes address)."""

    def __init__(self, session: AsyncSession):
        super().__init__(ClientDb, session)

    async def get_by_name(self, name: str) -> ClientDb | None:
        result = await self.session.execute(
            select(ClientDb).where(ClientDb.name == name)
        )
        return result.scalar_one_or_none()
```

### Lo que provee `BaseService` (no reimplementar)

| Método | Comportamiento |
|--------|---------------|
| `get_by_id(id)` | `session.get(model, id)` |
| `get_all()` | `select(model)` completo |
| `create(data: dict)` | add + commit + refresh |
| `update(id, data: dict)` | patch parcial + commit + refresh; `None` si no existe |
| `delete(id)` | soft delete si tiene `active`, hard delete si no; `None` si no existe |

`update` recibe `dict`. Hacer `.model_dump(exclude_unset=True)` en el router antes de llamarlo.  
`delete` retorna la entidad, no `bool`.

### Factory en `services/__init__.py`

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.client_service import ClientService

def get_client_service(session: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService(session)
```

---

## Lifespan (`app.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    from db.database import init_db, dispose_db
    try:
        await init_db()
        logger.info("Startup OK")
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise
    yield
    await dispose_db()
    logger.info("Shutdown OK")
```

`app.state` **no se usa para services con DB**. Una sesión no puede vivir toda la vida de la app.  
Para acceso fuera del ciclo de request (healthcheck, script puntual):

```python
async def run_once():
    async with get_sessionmaker()() as session:
        service = ClientService(session)
        result = await service.get_all()
        await session.commit()
    return result
```

---

## Routers (`routers/<domain>_router.py`)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.client import ClientDto, ClientCreateDto, ClientUpdateDto
from services import get_client_service
from services.client_service import ClientService
from logs import get_logger

router = APIRouter(prefix="/clients", tags=["clients"])
logger = get_logger()


@router.get("/", response_model=List[ClientDto], summary="List all clients")
async def list_clients(service: ClientService = Depends(get_client_service)):
    return await service.get_all()


@router.get("/{client_id}", response_model=ClientDto, summary="Get client by ID")
async def get_client(client_id: int, service: ClientService = Depends(get_client_service)):
    client = await service.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.post("/", response_model=ClientDto, status_code=status.HTTP_201_CREATED, summary="Create client")
async def create_client(data: ClientCreateDto, service: ClientService = Depends(get_client_service)):
    return await service.create(data.model_dump())


@router.patch("/{client_id}", response_model=ClientDto, summary="Update client")
async def update_client(client_id: int, data: ClientUpdateDto, service: ClientService = Depends(get_client_service)):
    client = await service.update(client_id, data.model_dump(exclude_unset=True))
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete client")
async def delete_client(client_id: int, service: ClientService = Depends(get_client_service)):
    if not await service.delete(client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
```

---

## Configuración de DB (`config.py`)

```toml
# config.toml — SQLite local
[database]
DB_TYPE = "sqlite3"
DB_NAME = "db.sqlite3"

# config.prod.toml — Postgres
[database]
DB_TYPE = "postgresql"
DB_DRIVER = "asyncpg"
DB_USER = "user"
DB_PASSWORD = "pass"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mydb"
```

`Database.url` genera la URL correcta según `DB_TYPE`. Rotar de motor = cambiar el `.toml`.  
`DB_DRIVER` vacío usa el default: `aiosqlite` para sqlite, sin driver extra para otros.

---

## Reglas transversales

1. **Todo async**: engine, sessionmaker, session, service methods, router handlers.
2. **`lazy="selectin"`** en relationships frecuentes. Nunca `lazy="select"` en async.
3. **`HTTPException` solo en routers**. Services retornan `None` para not-found.
4. **`exclude_unset=True`** en updates parciales.
5. **`model_config = {"from_attributes": True}`** en todos los Dto de respuesta.
6. **Logs en inglés** via `get_logger()`. Nunca `print()` en producción.
7. **Docstrings en inglés** en clases y métodos de service.
8. Un aggregate root = un archivo en cada capa. No mezclar dominios.
9. **Sin Singleton en services**. Instancia por request via `Depends`.

---

## Checklist al generar una nueva entidad

- [ ] `db/db_models/<domain>.py` → `<Domain>Db(Base)` con relationships y `lazy="selectin"`
- [ ] Importar en `db/db_models/__init__.py` para que `create_all` lo detecte
- [ ] `models/<domain>.py` → `<Domain>Dto`, `<Domain>CreateDto`, `<Domain>UpdateDto`
- [ ] `services/<domain>_service.py` → `<Domain>Service(BaseService[<Domain>Db])`
- [ ] Factory en `services/__init__.py`
- [ ] `routers/<domain>_router.py` → CRUD completo
- [ ] Agregar router a `routers/__init__.py`