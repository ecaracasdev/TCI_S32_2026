# Changelog

Registro de cambios relevantes del proyecto. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Unreleased]

### Added

- `docker-compose.yml` en la raíz, con `Dockerfile` para `backend/` (Python 3.14 + uv) y `frontend/` (build de Angular servido con nginx). `docker compose up --build` levanta todo el stack desde un clone limpio (issue #29, M2). Verificado de punta a punta: backend responde `200` en `/health`, frontend responde `200` en `http://localhost:8080`.
- `.dockerignore` en `backend/` y `frontend/` para no copiar `node_modules`, `.venv`, `dist` ni logs al build.
- Sección "Cómo levantar el proyecto con Docker" en el README principal, más una sección de Docker en `backend/README.md` y `frontend/README.md`.
