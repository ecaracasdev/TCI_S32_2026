# Planificación de estimación del equipo

**Equipo (núcleo, 3 integrantes — ver `TEAM_CHARTER.md`):** Elias Caracas, Martin Carrasco y Nicolás Pieroni.

Por tamaño de equipo (`docs/cronograma_alumnos.md`, sección 5), el alcance base es: registrar uso de repuesto en reparación (RN-01, RN-02, RN-06), cargar stock recibido con ubicación (RN-08), reportar incidencia con QR de máquina, y autenticación con 3 roles. El equipo decidió además avanzar con el pedido de compra (RN-03, RN-04, RN-09), que en el cronograma de cátedra es alcance de un 5to integrante; se toma como ampliación voluntaria, no como reemplazo del alcance base.

## Estimación

Tamaños relativos por tipo de tarea, usados para ordenar el trabajo semana a semana:

| Tipo de tarea | Tamaño | Ejemplos |
| --- | --- | --- |
| Documentación de dominio / máquina de estado | S | T01-T05, T07, T08 |
| ADR / documentación de arquitectura | S | T06, T10 |
| Componente o vista de consulta (listado + detalle, sin mutación) | M | T12, T13, T18, T19 |
| Vista con mutación de datos (alta, formulario, flujo de varios pasos) | M-L | T11, T14, T15, T16, T17 |
| Corrección transversal (navegación, despliegue, infraestructura) | M | T09, T20 |
| Backend con reglas de negocio + persistencia + tests | L | Implementación real de RN-01, RN-02, RN-03, RN-06, RN-08 (pendiente, M4) |

La estimación es relativa (S/M/L), no en horas: el cronograma de la cátedra fija la fecha de cada muestra: lo que no entra en el tamaño de la muestra se corre a la siguiente, no se reduce el alcance de una regla de negocio a mitad de camino.

## Asignación

Cada integrante es dueño de al menos un caso de uso end-to-end (`docs/cronograma_alumnos.md`, sección 6). Distribución real a partir de las issues y PRs del repo:

| Integrante | Área / CU dueño | Tareas |
| --- | --- | --- |
| **Elias Caracas** | CUN-01 — Registrar uso de repuesto en una reparación (RN-01, RN-02, RN-06). Reportar incidencia. Pedidos de compra (consulta) y máquinas (consulta). | T01 (máquina de estado de Incidencia), T16, T17, T18, T19, T20, T05, T07 |
| **Martin Carrasco** | Vistas de stock/repuestos, reposición y generación de pedidos de compra. Reserva (modelado). Diagrama contextual. | T02 (máquina de estado de Reserva), T03, T11, T12, T13, T14, T15 |
| **Nicolás Pieroni** | Arquitectura (ADR), componentes compartidos y documentación de criterios de frontend. Pedido de compra (modelado). | T04 (máquina de estado de Pedido), T06, T09, T10 |

Pendiente de asignar entre el equipo: T08 (actores del dominio), el fix de alias `@shared` en tests (#44), y el CU + pantalla de carga de stock recibido con ubicación (RN-08, dueño todavía sin definir).

## Cronograma

Fechas fijadas por la cátedra (`docs/cronograma_alumnos.md`, sección 4); estado según el repo al 2026-11-11:

| Muestra | Fecha | Entregable | Estado |
| --- | --- | --- | --- |
| M1 — Documentación funcional | vie 11/09 | CU + especificación + actividad/secuencia + arquitectura + planificación + máquinas de estado de Incidencia, Reserva y Pedido | Atrasado: máquinas de estado de Incidencia (T01), Reserva (T02) y Pedido (T04) completas; diagramas del CU (T05) y planificación (T07) se cierran ahora; actores del dominio (T08) sin asignar |
| M2 — Contrato + esqueleto desplegado | vie 02/10 | Prototipo estático de 3 pantallas + contrato OpenAPI v0 + repo desplegado | Contrato OpenAPI v0 y `docker-compose`/Dockerfile mínimo entregados; el equipo saltó el prototipo estático y fue directo a pantallas reales en Angular (T11-T19) |
| M3 — SPA contra el contrato | vie 16/10 | SPA consumiendo el contrato + walking skeleton desplegado | Cubierto por las vistas reales (T11-T19), con mocks por `environment.useMockData` mientras el backend no expone todas las reglas |
| M4 — Backend + reglas + tests | vie 30/10 | API + repository + service layer + tests de RN-01, RN-02 y RN-05 + auth stub | Contrato OpenAPI y scaffold de backend (FastAPI + SQLAlchemy) existen; falta implementar las reglas de negocio y los tests obligatorios |
| M5 — Integración end-to-end | vie 13/11 | 2 CU end-to-end + auth real + Docker | En curso: T20 (navegación y recarga para la demo) es la tarea más urgente para que la demo funcione sin 404 |
| M6 — Congelamiento | vie 20/11 | Sin features nuevas, suite verde, Swagger publicado | Pendiente |
| FINAL — Entrega y defensa | lun 30/11 | Sistema desplegado + documentación + defensa individual | Pendiente |
