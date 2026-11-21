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

La clave de firma solo es obligatoria al usar el OAuth genérico o sus tokens firmados.

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

### Claves y variables de entorno

Las claves secretas no están en el repositorio: `config.toml` no las define y se leen de variables de
entorno.

| Clave | Variable de entorno | Cuándo es obligatoria | Largo mínimo |
| --- | --- | --- | --- |
| `AUTH_SIGNING_KEY` | `AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY` | Al usar las firmas de auth o habilitar OAuth genérico | 32 bytes |
| `CLAVE_JWT` | `AUTOCONFIG_SECRETS__CLAVE_JWT` | Con el JWT local habilitado | 32 bytes en HS256, 48 en HS384, 64 en HS512 |

Generá cada valor con `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`. Para correr sin Docker:

```bash
export AUTOCONFIG_SECRETS__AUTH_SIGNING_KEY=<clave> # solo para OAuth genérico o tokens de auth
export AUTOCONFIG_SECRETS__CLAVE_JWT=<otra clave>
export AUTOCONFIG_AUTH__JWT__HABILITADO=true   # solo si querés el login con JWT
uv run app.py
```

Con Docker, las pasa `docker-compose.yml` desde el archivo `.env` de la raíz (ver `.env.example`), junto con
`POSTGRES_PASSWORD`, que llega al backend como `AUTOCONFIG_DATABASE__DB_PASSWORD`. Dentro de Compose la
configuración es `config.docker.toml` (montado como `config.toml`): igual a `config.toml` salvo `[database]`,
que apunta al servicio `db` de PostgreSQL y no incluye la contraseña. `tests/test_config_docker.py` falla
si los dos archivos difieren en otra sección.

- **Nombre de la variable:** `AUTOCONFIG_<SECCIÓN>__<CAMPO>`, con doble guion bajo entre niveles y sin
  distinguir mayúsculas. Por ejemplo, `AUTOCONFIG_AUTH__JWT__HABILITADO=true`. Una variable que no
  corresponde a ningún campo hace fallar la carga de la configuración.
- **Precedencia:** el archivo de configuración gana sobre la variable, así que esta solo tiene efecto sobre
  los campos que el archivo no define. Por ejemplo, `config.toml` define `PORT`, por lo que
  `AUTOCONFIG_SERVER__PORT` se ignora. Por eso `config.toml` no trae las claves ni `HABILITADO`: así la
  variable puede definirlas. Si definís `AUTH_SIGNING_KEY` en un `config.<env>.toml` (que no se versiona), esa
  es la que se usa.
- **Si falta o es corta**, se emite una advertencia; al utilizarla, la operación falla. El JWT local valida su propia clave al habilitarse.
- **Migración:** `SECRET_KEY` sigue aceptándose como nombre anterior. Renombrala a `AUTH_SIGNING_KEY` conservando el valor para mantener las firmas existentes. Si ambas tienen valores distintos, no se puede usar la firma.
- **Tests:** `tests/conftest.py` define una clave anterior propia para las pruebas.

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

## Keycloak

La integración de Keycloak está deshabilitada en el backend y no se registra su
middleware ni su endpoint de ejemplo. Los valores históricos de `[auth.KEYCLOAK]`
se aceptan por compatibilidad, pero se ignoran incluso si `ENABLED = true`.
La entrega utiliza autenticación JWT local: activar Keycloak en una configuración
antigua no protege la aplicación ni sustituye al JWT local. Asegurate de habilitar
y configurar este último para proteger las rutas.

El código y las dependencias de la integración histórica se conservan por ahora;
no se ha validado su uso como alternativa activa.

## JWT local y roles

El backend también puede emitir JWT propios y consultar los roles desde la base
de datos. Con `docker compose`, ya viene habilitado (usa la `CLAVE_JWT` de `.env`). Sin Docker, definí
las variables de "Claves y variables de entorno" o copiá `config.toml` a `config.<environment>.toml`,
configurá una clave secreta distinta por entorno y activá el bloque `[auth.JWT]`.

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
| `-c`, `--config` | Nombre del entorno (por ejemplo `dev` carga `backend/config.dev.toml`; default: `default`) |
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

## Usuarios de demostración

Con el backend iniciado en Docker, ejecutar desde la raíz:

```bash
docker compose exec backend uv run --no-dev gestionar_acceso.py preparar-demo
```

El comando solicita una contraseña por usuario, sin mostrarla. Crea los roles
`operario_maquina`, `empleado_mantenimiento`, `encargado_mantenimiento` y
`gerencia_administracion` y las cuentas `operario@test`,
`empleado@test`, `encargado@test` y
`gerencia@test`. Al repetirlo conserva las cuentas y contraseñas
existentes. Si una cuenta existente no tiene el rol esperado, finaliza con
error para que se revise su asignación.

Para iniciar sesión, enviar correo y contraseña a `POST /auth/token` y usar el
token obtenido para consultar `GET /auth/me`. Con `docker compose` el JWT ya
está habilitado; el backend suelto lo deja deshabilitado salvo que se active
(ver "Claves y variables de entorno").

Para crear un usuario individual:

```bash
docker compose exec backend uv run --no-dev gestionar_acceso.py crear-usuario --rol operario_maquina
```

## Base de prueba

Para probar los endpoints contra datos reales, sin los mocks del frontend, se
puede cargar una base de prueba con datos del dominio. Con el backend iniciado
en Docker, ejecutar desde la raíz:

```bash
docker compose exec backend uv run --no-dev python datos_prueba.py
```

Fuera de Docker, desde `backend/` y con las variables de "Claves y variables de entorno" definidas:

```bash
uv run python datos_prueba.py
```

También se puede usar el atajo `uv run crear-dummy-db`. Ambos comandos aceptan
las mismas opciones, incluida `--config dummy`; la validación de secretos usa
la configuración del entorno y es la misma para ambos.

El comando crea las tablas y carga los datos en la base indicada por `DB_NAME`
en `config.toml` (por defecto, `backend/data/db.sqlite3`). Para usar otra
configuración, agregar `--config dev` para usar `backend/config.dev.toml`. Al iniciar el backend,
usar la misma configuración para consultar esa base.
Por ejemplo, copiar `config.toml` a `config.dummy.toml`, cambiar `DB_NAME`
en la sección `[database]` y ejecutar:

```bash
uv run python datos_prueba.py --config dummy
```

El comando muestra el destino sin incluir credenciales. Las rutas relativas de
SQLite se resuelven desde el directorio de ejecución. Para PostgreSQL, configurar
`DB_TYPE = "postgresql"`, `DB_DRIVER = "asyncpg"` y los parámetros de conexión;
la base de datos debe existir previamente. El comando crea las tablas dentro de
esa base, no crea la base PostgreSQL en el servidor. Este flujo aún requiere
verificación de integración contra una instancia PostgreSQL.

Para SQLite, si `DB_DRIVER` está vacío o no se especifica, se usa `aiosqlite`
automáticamente.

Los usuarios de prueba nuevos tienen la contraseña `test`; es una credencial
conocida, exclusiva para entornos de prueba. Los usuarios existentes se
reutilizan sin cambiar su contraseña y deben tener el rol esperado. Se cargan:

- Un usuario por rol (`operario@test`, `empleado@test`,
  `encargado@test` y `gerencia@test`) y un segundo operario
  (`operario2@test`).
- 18 máquinas, 10 ubicaciones y 13 repuestos, incluidos los fixtures del frontend, con la
  compatibilidad de cada repuesto por tipo de máquina.
- Stock por ubicación que coincide con sus movimientos: carga inicial,
  recepciones, consumos en reparaciones y una reserva planificada. Algunos
  repuestos quedan en el umbral mínimo o por debajo, para probar las alertas.
- 19 incidencias en cinco estados, con sus reparaciones, usos e informes de
  resolución, y pedidos de compra en cada estado.

Si la base ya tiene máquinas o repuestos, el comando no carga nada. Para
volver a los datos iniciales, `--recreate` borra las máquinas, el stock, las
incidencias, las compras y las reservas, sin tocar usuarios ni roles. Pide
confirmación, salvo que se agregue `--si`:

```bash
uv run python datos_prueba.py --recreate
```

La carga se ejecuta en orden desde `datos_prueba.py`. Sus etapas están en
`dummy_db/` y cada archivo reúne los datos de ejemplo y su construcción:

1. `paso_01_usuarios.py`: roles y usuarios.
2. `paso_02_catalogo.py`: tipos, máquinas, ubicaciones y repuestos.
3. `paso_03_incidencias.py`: incidencias, reparaciones y consumos.
4. `paso_04_compras.py`: pedidos y recepciones.
5. `paso_05_stock.py`: reservas, movimientos y existencias.

Las etapas comparten una sesión y los cambios de datos se confirman juntos al
final. Para cambiar una máquina de ejemplo, editar `MAQUINAS` en el paso 2;
la definición de columnas de la tabla está en `db/db_models/catalogo.py`.
Los correos `@test` son identificadores de prueba, no direcciones de entrega.

### Asignar un rol por correo

Desde `backend`, el comando agrega un rol existente sin quitar los demás:

```bash
uv run asignar-rol --user empleado@example.com --role empleado_mantenimiento -c dev
```

`-c` selecciona `config.dev.toml` (por defecto se usa `config.toml`). El correo se
busca sin distinguir mayúsculas. El usuario y el rol deben existir; repetir la
asignación no duplica el rol. Para reemplazar todos los roles, usar explícitamente
`gestionar_acceso.py reemplazar-roles`.

### Listar usuarios

```bash
uv run listar-usuarios -c dev
```

Muestra ID, correo, nombre y roles; quienes no tengan roles figuran como
`Sin roles`. Sin `-c` usa `config.toml`. La consulta no crea ni modifica tablas.
