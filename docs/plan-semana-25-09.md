# Plan de trabajo hasta el viernes 25/09

- **Estado:** Propuesto
- **Fecha:** 2026-09-18
- **Autor:** Elias Caracas

El lunes 21/09 y el viernes 25/09 no hay clase (el viernes es examen), por lo que el 25/09 funciona como checkpoint interno. La entrega real de M2 es el viernes 02/10.

Los dueños son una propuesta y se ajustan en la reunión de equipo. El alcance de los casos de uso está en `docs/adr-alcance-casos-de-uso.md`.

## Meta del viernes 25/09

- M1 cerrado (T04, T05, T07 y T08 completas y mergeadas).
- Los 3 casos de uso del núcleo documentados.
- Épicas y sub-issues creadas, con bloqueos cargados.
- `docker compose up` levantando algo.
- Primera versión de las dos pantallas que faltan.
- Borrador de endpoints del contrato OpenAPI.

## Plan por día

| Día | Elias | Martín | Nicolás |
| --- | --- | --- | --- |
| Lun 21 | Aprobar el PR del template de issues. Crear épicas y sub-issues. | Arrancar el mockup "Registrar uso de repuesto" (#26). | Ajustar el PR #30: mover CUN-02 a un PR aparte y renombrar el archivo. |
| Mar 22 | Reunión de equipo. | Reunión de equipo. | Reunión de equipo. |
| Mié 23 y jue 24 | Escribir el CU "Reportar incidencia". Dockerfile de backend y de frontend (#29). | T05 (diagramas de CUN-01). T07 (planificación). Seguir con #26. | Terminar T08. Escribir el CU "Cargar stock recibido". |
| Vie 25 | PRs abiertos y con review. Compose funcionando. | PRs abiertos y con review. | Mockup #27 arrancado. PRs abiertos y con review. |

## Bloqueos

- El mockup #27 espera al CU "Cargar stock recibido".
- El contrato OpenAPI v0 (#28) espera a los 3 CU del núcleo.
- El docker-compose espera a los Dockerfiles de backend y de frontend.

## Temas para la reunión del martes 22/09

- Alcance del núcleo y lugar de "Registrar un repuesto" (ver el ADR de alcance).
- Las 3 preguntas abiertas de T01: si `EnTriage` es un estado real, si existe `Cancelada` y si `Resuelta` es el estado final.
- Las decisiones abiertas de T04: aprobación humana del pedido, creación automática al llegar al umbral y momento de la notificación por correo.
- Traspaso de T05 de Nicolás a Martín, dado que Martín escribió CUN-01.

## Semana del 28/09 al 02/10

- Terminar el contrato OpenAPI v0 en `docs/spec/`.
- Completar los mockups de las dos pantallas restantes.
- Verificar `docker compose up` desde un clone limpio.
- Cerrar la entrega de M2.
