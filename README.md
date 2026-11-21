# 🌱 TCI_S32_2026

> **Trabajo de Campo Integrador · Desarrollo de Software 2026 · Comisión S32 · UTN FR La Plata**

## Integrantes

| Legajo | Nombre y apellido   | Email                  |
| ------ | ------------------- | ----------------------- |
| 34575  | ELIAS, CARACAS      | ecaracasdev@gmail.com   |
| 32520  | Martin, Carrasco    | carrascomartin532@gmail.com |
| 31064  | Pieroni, Nicolas    | pieroni.nico@gmail.com |

--

Este repo es la **base de operaciones** de tu TCI. Acá la cátedra va a publicar el **dominio**, la **spec** y las **actividades**. Tu equipo **no trabaja acá**: hace un **fork** de este repo y labura en el suyo, recibiendo las actualizaciones de acá al toque.

---

## 👋 ¿De qué va esto?

Vas a construir, en equipo, **un sistema informático completo** (frontend + backend + base de datos + seguridad + pruebas) con impacto real en la comunidad. No es un TP más: es EL proyecto del cuatrimestre, y empieza hoy.

> Y sí: el encuadre da un poquito de cagazo. **Perfecto.** Es señal de que va en serio. Del cagazo se sale laburando — en equipo, con método, y paso a paso. Por algo arrancamos por **Git y GitHub**: la herramienta que te deja equivocarte sin romper nada.

---

## 🎯 Cómo arrancar (en 3 pasos)

Todo el detalle paso a paso **te llega por mail**. Acá va la versión corta:

1. **Formá tu equipo** (3–5 personas) y elegí al **primer representante (integrador)**.
2. El representante hace el **fork** de este repo → listo, tienen su repo grupal.
3. Cada integrante se registra en el **README del equipo** (legajo · nombre · email) por **Pull Request** con revisión de un compañero.

> 📬 **El detalle (fork, clone, `upstream`, TEAM_CHARTER, CONTRIBUTING, práctica de feature branch flow) está en el mail que te acaba de llegar.** No te saltes la lectura: es la que te prepara para el Multiple Choice del **lunes 31/08**.

---

## 🗂️ Estructura del repo (qué va a haber acá)

| Ruta            | Qué es                                                 |
| --------------- | ------------------------------------------------------ |
| `README.md`     | Esta portada                                           |
| `docs/dominio/` | El **dominio** del TCI (cuando la cátedra lo publique) |
| `docs/spec/`    | La **spec** (requerimientos y criterios)               |
| Actividades     | Consignas y material de cada etapa                     |

> ⚠️ **Ojo:** esta estructura crece a medida que avanza el cuatrimestre. Mantené tu fork **al día** con:
>
> ```bash
> git pull upstream main
> ```

---

## 🔀 Una decisión de diseño (para que la tengas clara)

Trabajamos con **forks + `upstream`** (el flujo de colaboración real del open source):

```
   TÚ (cátedra) ──pushea──►  desasoftfrlptn/TCI_S32_2026   (este repo)
        ▲                            │
        │  solo recibís (pull)       ▼
        │                  cada equipo: TU_USUARIO/TCI_S32_2026  (tu fork)
```

- Los PR de tu equipo van **siempre al `main` de tu fork**, **nunca** acá.
- Este repo es de **dónde recibís**, no a dónde mandás.

> Es el mismo flujo que usan millones de proyectos open source. Aprendélo bien: no te va a servir solo para esta cursada.

---

## ✨ La filosofía detrás (en serio)

- **Leer se hace en casa; hacer se hace en equipo.** La actividad asincrónica ES lectura — no hay atajo.
- **La IA asiste, el humano dirige y revisa.** Un PR bien revisado es el control de calidad que la IA no reemplaza.
- **Equivocarse es parte del método.** Por eso Git te deja volver atrás. La madurez está en revisar, corregir y seguir.
- **El respeto se construye en el código y en la gente.** Contrato de equipo, review entre pares, y cero entregas al voleo.

---

## 🐳 Cómo levantar el proyecto con Docker

> Paso a paso completo (datos de prueba, usuarios por rol, acceso a la base, tests y problemas comunes): [`docs/demo/levantar.md`](docs/demo/levantar.md). Guion de la demo: [`docs/demo/guion.md`](docs/demo/guion.md).

Desde un clone limpio, con Docker instalado y corriendo:

```bash
cp .env.example .env
```

Abrí `.env` y completá `CLAVE_JWT` y `POSTGRES_PASSWORD` (`AUTH_SIGNING_KEY` solo si usás las firmas del OAuth genérico). Generá cada valor con
`python3 -c "import secrets; print(secrets.token_urlsafe(48))"` (mínimo 32 bytes para cada clave de firma que se utilice). El
archivo `.env` no se versiona: las claves y la contraseña no están en el repositorio. Después:

```bash
docker compose up --build
```

Si falta alguna clave, `docker compose` no arranca y dice cuál. El compose activa el login con JWT
usando `CLAVE_JWT`; más detalle en "Claves y variables de entorno" de `backend/README.md`.

Esto levanta:

| Servicio | URL | Qué es |
| --- | --- | --- |
| `db` | (solo dentro de Compose) | PostgreSQL 16. El backend espera a que esté sano antes de arrancar. |
| `backend` | http://localhost:8300 | API FastAPI. `/health` devuelve `OK` y `/docs` muestra el Swagger. |
| `frontend` | http://localhost:8080 | SPA Angular servida con nginx (build de producción). |

Para pararlo: `docker compose down` desde la raíz del repo.

Los datos quedan en PostgreSQL, en el volumen `pgdata`: `docker compose down` los conserva y `docker compose down -v` los borra. La base arranca vacía; para cargar los datos de prueba, ver "Base de prueba" en `backend/README.md`. Dentro de Compose el backend usa `backend/config.docker.toml`, que es igual a `config.toml` salvo la sección `[database]`. Sin Docker y en los tests se sigue usando SQLite. Por qué: [`docs/M6-adr-sqlite-o-postgres.md`](docs/M6-adr-sqlite-o-postgres.md).

> **Si ya lo tenías levantado con SQLite:** los datos del volumen `backend-data` no pasan solos a PostgreSQL. Después del primer `docker compose up --build` con esta versión, volvé a cargar los datos de prueba. El volumen viejo se puede borrar con `docker volume rm tci_s32_2026_backend-data`.

> **En Mac con Colima:** si `docker compose up` falla porque el daemon no responde, asegurate de que Colima esté corriendo (`colima start`). Si `colima start` falla con `failed to attach disk "colima", in use by instance "colima"`, un simple `colima stop && colima start` no siempre alcanza — en ese caso `colima delete` (recrea la VM desde cero, perdés las imágenes cacheadas) seguido de `colima start` lo resuelve.

Detalle de cada subproyecto por separado (sin Docker) en `backend/README.md` y `frontend/README.md`.

---

## 🧩 Alcance académico

| Resultado de aprendizaje | Qué toca                                        |
| ------------------------ | ----------------------------------------------- |
| **RA03**                 | Uso de herramientas de desarrollo (Git, GitHub) |
| **RA04**                 | Administración del seguimiento (PR, review)     |
| **RA07**                 | Asistencia entre pares (revisión de código)     |

_Comisión S32 · Desarrollo de Software 2026 · UTN FR La Plata · Aula invertida + TCI._
