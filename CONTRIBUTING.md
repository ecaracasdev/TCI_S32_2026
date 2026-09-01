# 🛠️ CONTRIBUTING.md

> Cómo colaborar en este repo — modelo de ramas, convenciones y flujo de PRs.

## Modelo de ramas: Feature Branch Flow

Convención del TCI: **una feature = una rama = un PR**.

- Cada cambio (funcionalidad, fix, doc) se desarrolla en su propia rama.
- Esa rama se abre como un único Pull Request contra `main`.
- No se mezclan cambios de distinto propósito en la misma rama/PR.

## Nombrar una rama

Usá un nombre claro que indique el tipo de cambio y una descripción corta:

```
<tipo>/<descripcion-corta>
```

Ejemplos:

- `feat/login-usuario`
- `fix/validacion-email`
- `docs/team-charter`

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
git checkout -b feat/mi-feature main
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
