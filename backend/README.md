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
    fastapi-keycloak-middleware python-keycloak jwcrypto \
    uvicorn[standard] "rich>=13,<15" ruamel.yaml tomlkit tomli typer
```

---

## Docker

Para correrlo suelto (sin el frontend), desde esta carpeta:

```bash
docker build -t tci-backend .
docker run -p 8300:8300 tci-backend
```

Para levantar todo el stack (backend + frontend) juntos, usar `docker compose up --build` desde la raíz del repo — ver el README principal.

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

## JWT local y roles

El backend también puede emitir JWT propios y consultar los roles desde la base
de datos. Para habilitarlo, copiá `config.toml` a `config.<environment>.toml`,
configurá una clave secreta distinta por entorno y activá el bloque `[auth.JWT]`.
No habilites al mismo tiempo el proveedor JWT local y Keycloak.

```toml
[secrets]
CLAVE_JWT = "<secreto aleatorio de al menos 32 bytes para HS256>"

[auth]
ENABLED = true

[auth.JWT]
HABILITADO = true
DURACION_TOKEN_MINUTOS = 30
ALGORITMO = "HS256"
ALGORITMOS_PERMITIDOS = ["HS256", "HS384", "HS512"]
RUTAS_EXCLUIDAS = [
    "^/$",
    "^/health$",
    "^/docs(?:/.*)?$",
    "^/redoc(?:/.*)?$",
    "^/openapi\\.json$",
    "^/auth/token$",
]
```

`HS256`, `HS384` y `HS512` son los algoritmos HMAC admitidos. El algoritmo
seleccionado debe aparecer en `ALGORITMOS_PERMITIDOS`; la aplicación valida los
JWT únicamente con ese algoritmo. La clave requiere 32, 48 o 64 bytes como
mínimo para HS256, HS384 o HS512 respectivamente.

`POST /auth/token` recibe un formulario
`application/x-www-form-urlencoded` con `grant_type=password`, `username`
(correo) y `password`. Devuelve `access_token`, `token_type` y `expires_in`
en segundos. Las credenciales incorrectas devuelven HTTP 400 con
`{"error":"invalid_grant"}`. Este contrato local usa el formato histórico
del endpoint de token, con el alcance limitado al login propio de la aplicación.

El JWT firmado contiene `iss`, `sub`, `aud`, `iat`, `exp`, `jti` y una
copia de los roles al emitirlo. `auth.JWT.EMISOR` y `auth.JWT.AUDIENCIA`
configuran los valores que valida la API. Los tokens anteriores a este cambio
requieren volver a iniciar sesión. `GET /auth/me`, con
`Authorization: Bearer <access_token>`, devuelve ID, nombre, apellido,
correo y roles actuales para cargar el perfil.
Las rutas que no coinciden con `RUTAS_EXCLUIDAS` requieren un token válido. Las
dependencias `obtener_usuario_actual` y `requiere_rol(...)` están disponibles
para proteger routers; `requiere_rol` consulta los roles vigentes en la base.

Para rutas opcionales, usar `obtener_usuario_actual_opcional` y agregar el patrón
de esa ruta a `RUTAS_EXCLUIDAS`. Sin Bearer devuelve `None`; si se envía uno, la
dependencia valida el token y carga el usuario. Para consultas dentro de código,
están disponibles `usuario_tiene_rol`, `usuario_tiene_algun_rol`,
`usuario_tiene_todos_los_roles` y `usuario_tiene_atributo`. También se pueden
proteger rutas con `requiere_atributo("verificado", True)`. Los atributos
consultables están limitados a datos públicos del usuario; el hash de contraseña
no se puede inspeccionar con esta utilidad.

```python
from fastapi import Depends

from autorizacion_roles import (
    obtener_usuario_actual,
    obtener_usuario_actual_opcional,
    requiere_rol,
)


@router.get("/privado")
async def privado(usuario=Depends(obtener_usuario_actual)):
    return {"correo": usuario.correo}


@router.get(
    "/mantenimiento",
    dependencies=[Depends(requiere_rol("empleado_mantenimiento"))],
)
async def mantenimiento():
    return {"permitido": True}


@router.get("/saludo")
async def saludo(usuario=Depends(obtener_usuario_actual_opcional)):
    return {"saludo": f"Hola {usuario.nombre}" if usuario else "Hola visitante"}
```

Las tablas de autorización se llaman `usuarios`, `roles` y `usuarios_x_roles`;
las tablas pivot siguen la convención `tabla_a_x_tabla_b`. Si la base ya tenía
las tablas `users`, `role_x_user_db` o `usuarios_roles`, el arranque las renombra
antes de crear el esquema nuevo. Para dar de alta usuarios y roles se
pueden usar los comandos locales de `gestionar_acceso.py` o los métodos de
`ServicioAutenticacion`. Las rutas administrativas de gestión se incorporarán
en una tarea posterior.

```bash
uv run python gestionar_acceso.py crear-rol empleado_mantenimiento
uv run python gestionar_acceso.py crear-usuario --nombre Ana --apellido Pérez \
    --genero F --correo ana@example.com --rol empleado_mantenimiento
uv run python gestionar_acceso.py reemplazar-roles 1 --rol encargado_mantenimiento
```

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
