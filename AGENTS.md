# AGENTS.md

Guía para cualquier agente (Claude Code u otro) que trabaje en este repositorio.

## Remotos — regla crítica

- `origin` = `ecaracasdev/TCI_S32_2026` — el fork del equipo. **Acá van todos los PR e issues.**
- `upstream` = `desasoftfrlptn/TCI_S32_2026` — el repo de la cátedra, **de solo lectura**. Nunca se le pushea ni se le abre un PR.
- Todo comando `gh` debe llevar `--repo ecaracasdev/TCI_S32_2026` explícito — `gh` puede resolver al repo equivocado si no se especifica.
- Antes de cualquier push, verificar la URL completa del remoto (no confiar solo en el alias `origin`), y después confirmar con `gh pr view <numero> --repo ecaracasdev/TCI_S32_2026 --json isCrossRepository` que da `false`.

## Stack del proyecto

Decidido en el ADR `docs/T06-adr-arquitectura.md` (aprobado por el profesor), **no coincide con lo que sugiere el cronograma de la cátedra**:

- Frontend: **Angular 21** + TypeScript (no React).
- Backend: **FastAPI** + Python 3.14, gestor de paquetes **uv** (no pip/poetry).
- Persistencia: **SQLAlchemy** con DTOs separados (no SQLModel).
- Base de datos: SQLite en desarrollo (`aiosqlite`), PostgreSQL como objetivo.

## Convenciones de Git

- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`) — ver `TEAM_CHARTER.md`.
- Branches: `<tipo>/<descripcion-corta>`.
- PRs: mínimo 1 aprobación de alguien que no sea el autor. El autor nunca se automergea (lo impone tanto el charter como el ruleset de GitHub).
- `main` está protegida por un ruleset de GitHub — no se permite push directo, solo merge de PR aprobados.
- **Nunca agregar atribución de IA** ("Generated with Claude Code", `Co-Authored-By: Claude...") en commits, PRs ni comentarios — en ningún repo, no solo en este.

## Gotchas técnicos conocidos

- **`git checkout` entre ramas puede borrar archivos del disco.** Si un archivo está trackeado solo en la rama de origen y no en la de destino, git lo elimina del working tree al cambiar de rama (pasó dos veces en este proyecto: con el scaffold de `investigacion/` y con `node_modules`). Si hay cambios sin pushear en una rama, pushearlos *antes* de cambiar de rama.
- **Colima (Docker en esta Mac) puede fallar al arrancar** con `failed to attach disk "colima", in use by instance "colima"` incluso sin otra instancia corriendo. No se resolvió reintentando `colima start`/`stop` ni matando procesos colgados (`limactl usernet`, `colima daemon`) desde una sesión de agente — hay que probarlo en una Terminal real del usuario, no asumir que es un problema de proceso colgado sin más.
- El backend (`backend/app.py`) levanta sin Docker con `uv sync --no-dev && uv run app.py --host 0.0.0.0` — confirmado, responde `/health` con `200 OK`. Útil para probar cambios del backend sin pasar por Docker.
- El build de Angular (`frontend/`) deja el output en `dist/ng-21-app-template/browser` (no asumir la ruta, confirmarla con `find dist` después de `npm run build`).
- El repo no tiene `.gitignore` en la raíz por defecto en ramas viejas — si aparecen cientos de archivos de `node_modules` como "sin trackear" en una rama, probablemente sea por esto.

## Estructura relevante

- `docs/dominio/dominio.md` — fuente de verdad del dominio funcional.
- `docs/cronograma_alumnos.md` — fechas y alcance de cada muestra (M1 a M6).
- `docs/caso-de-uso.md`, `docs/estado-incidencia.md`, etc. — documentación de M1.
- `backend/`, `frontend/` — scaffolds reales (FastAPI y Angular), sin lógica de negocio todavía.
- `docs/maquetado/` — prototipo HTML/CSS estático (M2), independiente del scaffold de Angular.
- `investigacion/` — tickets individuales de investigación de cada integrante, en ramas personales (`investigacion/<apellido-nombre>`), sin PR.
