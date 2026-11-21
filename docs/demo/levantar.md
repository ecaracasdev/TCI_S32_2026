# Levantar y probar el sistema

Pasos para levantar el sistema completo en tu máquina con Docker, cargar los datos de prueba y correr los tests. Todos los comandos se corren desde la **raíz del repositorio** (la carpeta donde está `docker-compose.yml`), salvo que el paso indique otra. El guion de la demo está en [`guion.md`](guion.md).

## Requisitos

| Para | Necesitás |
| --- | --- |
| Levantar el sistema | Docker con Docker Compose (Docker Desktop, o Colima en Mac), git y `python3` |
| Probar la API desde la terminal | `curl` y `jq` (en Mac: `brew install jq`) |
| Correr los tests del backend | [`uv`](https://docs.astral.sh/uv/) |
| Correr los tests del frontend | Node.js con npm |

Los comandos son para bash o zsh (Mac o Linux). En Windows, usá Git Bash o WSL.

## 1. Traer la última versión

```bash
git switch main
git pull
```

## 2. Crear el `.env` (solo la primera vez)

El `.env` lleva la clave JWT del backend y la contraseña de PostgreSQL; `AUTH_SIGNING_KEY` solo es necesaria para el OAuth genérico. No se versiona. Este comando lo crea con valores aleatorios:

```bash
python3 -c "import secrets; print('\n'.join(f'{k}={secrets.token_urlsafe(48)}' for k in ('CLAVE_JWT', 'POSTGRES_PASSWORD')))" > .env
```

Si ya tenías un `.env` con `CLAVE_JWT`, alcanza con agregarle la contraseña:

```bash
echo "POSTGRES_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
```

## 3. Acceso a la base desde DBeaver u otro cliente (opcional, solo la primera vez)

PostgreSQL queda solo dentro de Docker. Si querés conectarte con DBeaver, este archivo local publica su puerto en el **5433** de tu máquina, solo para tu máquina (`127.0.0.1`, no para la red). La segunda línea hace que git lo ignore:

```bash
printf 'services:\n  db:\n    ports:\n      - "127.0.0.1:5433:5432"\n' > docker-compose.override.yml
echo "docker-compose.override.yml" >> .git/info/exclude
```

`docker compose` lo lee solo, sin flags. Si ya tenías el sistema levantado, aplicalo con `docker compose up -d db`: recrea solo la base y conserva los datos.

## 4. Levantar

```bash
docker compose up -d --build
docker compose ps
```

Tienen que aparecer tres servicios: `db` (healthy), `backend` y `frontend`. El primer build tarda unos minutos, y después el backend tarda unos segundos más en arrancar. Para confirmar que usa PostgreSQL (si no muestra nada, esperá unos segundos y repetilo):

```bash
docker compose logs backend | grep DatabaseType
```

Tiene que decir `postgresql`.

| Qué | Dónde |
| --- | --- |
| Frontend | http://localhost:8080 |
| API | http://localhost:8300 |
| Swagger | http://localhost:8300/docs |
| Salud | http://localhost:8300/health |

## 5. Cargar los datos de prueba

La base arranca vacía. Este comando crea los usuarios de prueba y carga los datos del dominio:

```bash
docker compose exec backend uv run --no-dev crear-dummy-db
```

Carga 18 máquinas, 10 ubicaciones, 13 repuestos, 19 incidencias, 9 pedidos de compra y 3 reservas. Si la base ya tiene datos, no carga nada ni toca los usuarios.

| Usuario | Contraseña | Rol | Qué ve en el menú |
| --- | --- | --- | --- |
| `operario@test` | `test` | Operario de máquina | Inicio, Reportar incidencia e Incidencias |
| `empleado@test` | `test` | Empleado de mantenimiento | Inicio, Incidencias, Registrar uso, Máquinas, Repuestos, Ubicaciones, Reposición y Compras; toma y resuelve incidencias |
| `encargado@test` | `test` | Encargado de mantenimiento | Inicio, Incidencias, Máquinas, Repuestos, Ubicaciones, Reposición, Compras y Pedidos de compra; además da de alta y edita máquinas, libera reservas y aprueba o cancela pedidos |
| `gerencia@test` | `test` | Gerencia / Administración | Lo mismo que el encargado, solo lectura |

Los permisos completos están en [`docs/actores.md`](../actores.md).

Para volver a los datos iniciales (borra y recarga máquinas, stock, incidencias, reservas y movimientos; no toca los usuarios):

```bash
docker compose exec backend uv run --no-dev crear-dummy-db --recreate --si
```

## 6. Mirar la base

**Desde DBeaver** (requiere el paso 3): Nueva conexión → PostgreSQL.

| Campo | Valor |
| --- | --- |
| Host | `localhost` |
| Puerto | `5433` |
| Base de datos | `tci` |
| Usuario | `tci` |
| Contraseña | el valor de `POSTGRES_PASSWORD` (verlo con `grep POSTGRES_PASSWORD .env`) |

Las tablas están en el esquema `public`. Las más útiles: `incidencias`, `repuestos`, `repuestos_x_ubicaciones` (físico y reservado por ubicación), `reservas`, `items_reserva` y `movimientos_stock`.

**Desde la terminal:**

```bash
docker compose exec db psql -U tci -d tci -c "\dt"
docker compose exec db psql -U tci -d tci -c "select codigo, nombre, stock_minimo from repuestos;"
docker compose exec db psql -U tci -d tci -c "select tipo_movimiento, cantidad, variacion_fisica, variacion_reservada from movimientos_stock order by id desc limit 10;"
```

## 7. Probar la API con curl

Primero los tokens:

```bash
API=http://localhost:8300
token() { curl -s -X POST $API/auth/token -d "username=$1@test&password=test&grant_type=password" | jq -r .access_token; }
EMP=$(token empleado)
OPE=$(token operario)
```

Algunas consultas:

```bash
curl -s $API/api/v0/maquinas -H "Authorization: Bearer $EMP" | jq '.total'
curl -s $API/api/v0/repuestos/codigo/REP-00087 -H "Authorization: Bearer $EMP" | jq '{codigo, stock_fisico_total, stock_reservado_total, stock_disponible_total}'
curl -s $API/api/v0/stock/alertas -H "Authorization: Bearer $EMP" | jq '[.items[] | {codigo: .repuesto.codigo, disponible: .stock_disponible, minimo: .stock_minimo}]'
curl -s "$API/api/v0/incidencias?limit=3" -H "Authorization: Bearer $OPE" | jq '[.items[] | {id, maquina: .maquina.codigo, estado}]'
curl -s -o /dev/null -w "%{http_code}\n" $API/api/v0/reservas    # sin token: 401
```

Las reservas paso a paso están en el [guion](guion.md#5-reservas-rn-05-y-rn-10-3-minutos).

## 8. Correr los tests

Backend (usan SQLite, no hace falta Docker):

```bash
cd backend
uv sync
uv run pytest -q
```

Solo los de una regla, con el detalle de cada test:

```bash
uv run pytest tests/test_reservas.py -v
```

Frontend:

```bash
cd frontend
npm install
npx ng test --watch=false
```

## 9. Parar y limpiar

```bash
docker compose down        # para todo y conserva la base
docker compose down -v     # para todo y BORRA la base (volumen pgdata)
```

## 10. Problemas comunes

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `Falta POSTGRES_PASSWORD` (o `CLAVE_JWT`) | No existe el `.env` o le falta ese valor | Paso 2 |
| `port is already allocated` en 8080 u 8300 | Otro contenedor o programa usa ese puerto | `docker ps` para ver cuál y pararlo |
| El login falla con usuario y contraseña correctos | La base está vacía | Paso 5 |
| El login falla con `@test` / `test`, pero la base tiene datos | La base se cargó con una versión anterior de los datos de prueba | `docker compose down -v`, `docker compose up -d` y el paso 5 |
| DBeaver: `Connection refused` en 5433 | Falta el paso 3 o no se aplicó | Paso 3 y `docker compose up -d db` |
| DBeaver: `password authentication failed` | La base se creó con otra contraseña (el `.env` cambió después) | `docker compose down -v` la borra y se recrea con la del `.env`; después, el paso 5 |
| `docker compose` no responde (Mac con Colima) | Colima apagado | `colima start` |
| `failed to attach disk "colima"` | Problema conocido de Colima | `colima stop && colima start` en una terminal propia; si sigue, `colima delete` y `colima start` (se pierden las imágenes cacheadas) |
