# Proyecto

> Descripción breve del proyecto.

---

## Requisitos

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (recomendado) o pip

---

## Instalación

```bash
# Con uv (recomendado)
uv sync

# Con pip
pip install "fastapi[standard]" sqlalchemy aiosqlite jinja2 \
    fastapi-keycloak-middleware python-keycloak \
    uvicorn[standard] "rich>=13,<15" ruamel.yaml tomlkit tomli typer
```

---

## Configuración

Copiá el archivo de configuración base y ajustá los valores:

```bash
cp config.toml config.dev.toml
```

Los archivos de configuración siguen la convención `config.<env>.toml`.  
El archivo activo se selecciona con `-c <nombre>` al iniciar (default: `default`).

### Autoconfig local

La plantilla incluye una copia local de `autoconfig/`, por lo que no se instala
la librería como paquete independiente. La definición declarativa está en
`config.py` y la API existente de `utils.py` se mantiene como adaptador para
`load_config`, `get_config` y `update_config`.

La copia local conserva la generación y validación de archivos TOML, YAML y
JSON, además de variables de entorno con prefijo `AUTOCONFIG_`. Sus
dependencias de runtime sí están declaradas en `pyproject.toml` y se instalan
normalmente con `uv sync` o `pip`.

---

## Ejecución

```bash
# Básico
python app.py

# Con opciones
python app.py -c dev -p 8080 -H 0.0.0.0 -d

# Sin volcado a archivo de logs
python app.py --no-logs
```

## Keycloak y autorización

La plantilla usa el header estándar:

```text
Authorization: Bearer <access-token>
```

Activá `[auth.KEYCLOAK].ENABLED` en el archivo de configuración del entorno y
completá `URL`, `REALM` y `CLIENT_ID`. El middleware valida el token contra la
clave pública del realm y deja disponible un `KeycloakUser` compatible con
diccionario:

```python
from fastapi import Depends

from auth_utils import (
    KeycloakUser,
    get_current_user,
    require_client_role,
    require_group,
    require_realm_role,
    require_role,
    username_equals,
)


@router.get("/me")
async def me(user: KeycloakUser = Depends(get_current_user)):
    return {
        "id": user.user_id,
        "username": user.username,
        "realm": user.realm,
        "roles": user.roles,
        "realm_roles": user.realm_roles,
        "client_roles": user.client_roles,
        "groups": user.groups,
    }


@router.get(
    "/admin",
    dependencies=[Depends(require_client_role("admin"))],
)
async def admin_area():
    return {"status": "allowed"}


@router.get(
    "/team",
    dependencies=[Depends(require_group("/engineering"))],
)
async def engineering_area():
    return {"status": "allowed"}
```

También están disponibles `require_realm_role`, `require_role` con
`source="realm" | "client"`, `require_permission` y `username_equals`. Las
validaciones devuelven `401` cuando falta o es inválido el token y `403` cuando
el usuario autenticado no cumple la condición.

La ruta `GET /auth/me` sirve como ejemplo y devuelve el objeto normalizado.

### Flags disponibles

| Flag | Descripción |
|---|---|
| `-c`, `--config` | Nombre del archivo de config a cargar (default: `default`) |
| `-p`, `--port` | Puerto del servidor |
| `-H`, `--host` | Host del servidor |
| `-d`, `--debug` | Activa modo debug |
| `-n`, `--no-logs` | Deshabilita volcado a archivo (stdout sigue activo) |
| `-R`, `--restrict-modules` | Lista de módulos a excluir del registro |

---

## Estructura

```
.
├── app.py                  # Entry point, bootstrap y configuración de FastAPI
├── autoconfig/              # Copia local de la librería de configuración
├── config.py               # Modelos Pydantic de configuración
├── config.toml             # Config base
├── config.dev.toml         # Config de desarrollo
├── utils.py                # Adaptador de compatibilidad sobre autoconfig
├── logs.py                 # Logger singleton
├── db/
│   ├── database.py         # Engine y sesión de SQLAlchemy
│   └── db_models/          # Modelos ORM
│       ├── base.py
│       └── product.py
├── models/                 # Schemas Pydantic (request/response)
│   └── product.py
├── routers/                # Routers de FastAPI
│   └── base_router.py
├── services/               # Lógica de negocio
│   ├── auth.py
│   └── base.py
└── logs/                   # Archivos de log generados en runtime
```

---

## Convenciones de git

### Commits

Los commits usan emojis para categorizar cambios:

| Tipo | Descripción |
|---|---|
| ⭐ `RELEASE` | Versión final con integración de funcionalidades |
| 🔒 `STABLE` | Versión estable o probada de una funcionalidad |
| ➕ `ADD` | Nuevo desarrollo sobre una funcionalidad existente |
| 🔧 `MOD` | Modificación de código existente |
| ✨ `REF` | Refactorización para mejorar estructura o rendimiento |
| 🐛 `FIX` | Corrección de un error específico |

```bash
git commit -m "🐛 Fix de button guardar en pantalla de inicio ticket_1203"
```

### Ramas

| Rama | Uso |
|---|---|
| `main` | Estado estable y productivo del proyecto |
| `feature/<nombre>` | Desarrollo de una funcionalidad o característica |
