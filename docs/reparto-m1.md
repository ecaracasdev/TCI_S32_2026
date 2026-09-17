# Reparto de tareas — Milestone 1

**Equipo:** Elias Caracas, Martin Carrasco, Nicolás Pieroni
**Entrega:** viernes 11/09

## ⚠️ Paso 0 — bloqueante (una sola persona, ya)

```bash
git checkout main
git pull upstream main
git push origin main
```

Trae el dominio y el cronograma de la cátedra al fork. `docs/dominio/` y `docs/cronograma_alumnos.md` todavía no existen en `origin/main`. Avisar en el grupo apenas esté listo para que los otros dos hagan `git pull origin main` antes de crear su rama.

## Ya hecho

- `TEAM_CHARTER.md` y `CONTRIBUTING.md` mergeados
- README con los 3 integrantes
- CUN-01 "Registrar uso de repuesto" en `docs/caso-de-uso.md` (falta el escenario de excepción)
- `docs/planificacion.md` creado (todavía sin contenido)

## Para después de la M1

- Alinear stack a React + TypeScript + Vite, o ADR justificando otra cosa
- Revisar a mano si quedó algún PR viejo abierto contra el repo equivocado

## Elias

1. Confirmar que el Paso 0 quedó hecho y pusheado.
2. Habilitar GitHub Issues y crear el Project board en el fork.
3. Completar `docs/planificacion.md`: estimación, asignación y cronograma. Cargar las issues de esta lista.
4. Modelar la máquina de estado de **Incidencia** → `docs/T01-maquina-estado-incidencia`
5. Revisar y aprobar los PR de Martin y Nicolás (sin auto-merge).

## Martin

1. `git pull origin main` apenas Elias avise.
2. Leer `docs/dominio/dominio.md` completo, especialmente la sección 7.
3. Modelar la máquina de estado de **Reserva** → `docs/T02-maquina-estado-reserva`
4. Armar el diagrama contextual del sistema → `docs/T03-diagrama-contextual`
5. PR a `main` con review de un compañero.

## Nicolás

1. `git pull origin main` apenas Elias avise.
2. Leer `docs/dominio/dominio.md`, sección 7.
3. Modelar la máquina de estado de **Pedido** → `docs/T04-maquina-estado-pedido`
4. Completar el CUN-01: agregar el escenario de excepción + diagrama de actividad/secuencia → `docs/T05-diagramas-cu-principal`
5. Redactar el ADR de arquitectura multicapa → `docs/T06-adr-arquitectura`

## Reglas rápidas

- **PR:** mínimo 1 review de un compañero, el autor no se auto-mergea (ver `TEAM_CHARTER.md`).
- **Ramas:** `<tipo>/<codigo>-<descripcion-corta>`.
- Los PR van siempre a `ecaracasdev/TCI_S32_2026`, nunca al repo de la cátedra.
