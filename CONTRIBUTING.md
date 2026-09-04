# 🛠️ CONTRIBUTING.md

> Cómo colaborar en este repo — modelo de ramas, convenciones y flujo de PRs.

## Modelo de ramas: Feature Branch Flow

Convención del TCI: **una feature = una rama = un PR**.

Elegimos Feature Branch Flow como workflow del equipo por:

1. **Tamaño del equipo:** somos pocos integrantes, así que un flujo simple de una
   rama por feature es más fácil de coordinar que esquemas con múltiples ramas
   de larga vida (ej. Gitflow).
2. **Metodología ágil:** queremos control dinámico sobre features y fixes,
   iterando rápido, sin la sobrecarga de sincronizar varios entornos de
   desarrollo en paralelo.
3. **Despliegue:** no manejamos múltiples entornos (staging/producción
   separados) — un solo entorno de despliegue. Eso hace que `main` sea siempre
   la fuente de la verdad: estable y lista para desplegarse en cualquier
   momento, sin pasos de promoción entre ramas.

### Acciones que este flow nos exige

- `main` nunca se toca directo — siempre estable y desplegable.
- Cada historia/tarea = una rama nueva desde `main` actualizado.
- Commits chicos y frecuentes en la rama.
- Abrir PR de la rama a `main`.
- Al menos 1 review de un par; el autor no se auto-mergea.
- Merge a `main` y borrar la rama.

## Nombrar una rama

Usá un nombre claro que indique el tipo de cambio, el código de la tarea y una descripción corta:

```
<tipo>/<codigo>-<descripcion-corta>
```

Ejemplos:

- `feat/T12-login-usuario`
- `fix/T15-validacion-email`
- `docs/T20-workflow-justificacion`

## Nadie pushea directo a `main`

Todo cambio entra por **Pull Request**. La rama `main` está protegida: no acepta push directo, solo merges de PRs aprobados.

## ⚠️ A dónde van los PR

Los PR van **SIEMPRE** a la rama `main` del **fork de tu equipo** (`TU_USUARIO/TCI_S32_2026`), **NUNCA** al repo base de la cátedra (`desasoftfrlptn/TCI_S32_2026`).

El repo de la cátedra es de **donde solo recibís** (`pull`), nunca a donde mandás (`push`).

## Mantener el fork al día con la cátedra

Antes de arrancar una feature nueva, traé las novedades de la cátedra:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

Después, creá tu rama de feature desde `main` ya actualizado:

```bash
git checkout -b feat/T00-mi-feature main
```

## Convención de commits

Usamos **Conventional Commits** — ver detalle en [TEAM_CHARTER.md](./TEAM_CHARTER.md#convención-de-commits):

```
<tipo>: <descripción corta>
```

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## Revisión y aprobación de PRs

- **Mínimo 1 review** de un compañero antes de mergear.
- **El autor del PR no se mergea a sí mismo.**
- El/la reviewer deja comentarios en los archivos que necesiten cambios; el autor los resuelve antes de que se apruebe.
- Una vez aprobado y con conversaciones resueltas, cualquier integrante con acceso puede mergear (preferentemente el autor, una vez tiene el approve).
