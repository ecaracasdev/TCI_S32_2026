# CU: Cargar stock recibido con ubicación

## Identificación
- **ID**: CUN-02
- **Objetivo**: Registrar la recepción de un pedido de compra, cargando el stock físico y la ubicación de cada repuesto recibido
- **Prioridad**: Alta
- **Actor principal**: Encargado de mantenimiento
- **Actores secundarios**: Persona delegada (si el encargado delega la carga), Sistema de notificación (correo)

## Precondiciones
- El usuario está autenticado con rol Encargado de mantenimiento (o fue delegado por uno)
- Existe un pedido de compra en estado `Confirmado` o `PendienteDeRecepcion`
- El pedido tiene al menos una línea (ítem) todavía sin recibir por completo

## Postcondiciones (éxito)
- Se registró una recepción vinculada al pedido, con la cantidad y ubicación cargadas por cada línea recibida
- Se generó un movimiento de stock tipo entrada por cada línea recibida
- El stock físico de cada repuesto recibido quedó incrementado en la cantidad cargada
- Si todas las líneas del pedido quedaron completamente recibidas, el pedido pasa a estado `Recibido`; si falta alguna, permanece en `PendienteDeRecepcion`

## Escenario principal
1. El encargado abre el detalle de un pedido de compra en estado `Confirmado` o `PendienteDeRecepcion`
2. El sistema muestra las líneas del pedido con su cantidad solicitada y lo ya recibido en recepciones anteriores
3. El encargado indica, para una o más líneas, la cantidad recibida y la ubicación donde se guarda
4. El encargado puede delegar la carga en otra persona, quedando igual como responsable de supervisarla
5. El sistema valida que la cantidad cargada no supere lo pendiente de recibir en esa línea
6. El sistema registra la recepción con sus líneas
7. El sistema incrementa el stock físico de cada repuesto en la ubicación indicada
8. El sistema genera un movimiento de stock tipo entrada por cada línea, vinculado al pedido y a la recepción (RN-06)
9. El sistema evalúa si todas las líneas del pedido quedaron completas; si es así, marca el pedido como `Recibido`

## Escenario alternativo — recepción parcial
En el paso 3, si el encargado carga menos cantidad que la solicitada en una o más líneas:
- El sistema acepta la recepción parcial y la registra igual (pasos 6 a 8)
- El pedido permanece en `PendienteDeRecepcion`
- Las líneas y cantidades pendientes quedan disponibles para una recepción posterior

## Excepciones

| Paso | Excepción | Respuesta del sistema |
| --- | --- | --- |
| 1 | El pedido no está en estado `Confirmado` ni `PendienteDeRecepcion` | Rechaza la operación; no se puede registrar recepción sobre un pedido `Creado`, en revisión o `Cancelado` |
| 3 | La cantidad cargada es ≤ 0 o supera lo pendiente de recibir en esa línea | Rechaza el ingreso y pide una cantidad válida |
| 3 | No se indica una ubicación para una línea con cantidad > 0 | Rechaza la operación; toda cantidad recibida necesita una ubicación |
| 6 | Se intenta registrar dos veces la misma recepción | **Fuera de alcance de este CU.** El dominio exige que la transición se registre una sola vez para no duplicar stock (`docs/T04-maquina-estado.pedido.md`); la idempotencia de la carga queda para el backend (M4) |

## Reglas de negocio relacionadas

- **RN-08 — Carga de compra.** Al recibir una compra, se carga el stock físico y su ubicación; la tarea puede delegarse y supervisarse.
- **RN-06 — Trazabilidad.** La recepción queda vinculada al pedido de compra, para poder reconstruir la historia interna del repuesto (pedido → recepción → uso).
- **RN-09 — Notificación por correo.** Se notifica la recepción como parte de las solicitudes de compra con seguimiento (puerto de notificación con adaptador falso).

## Referencias

- `docs/dominio/dominio.md`, RN-08 y sección 7 (huecos deliberados: la decisión de "completitud" para pasar a `Recibido` es una propuesta del equipo).
- `docs/T04-maquina-estado.pedido.md`: transición `registrarRecepcion` → `Recibido` y la nota sobre registrar la transición una sola vez.
- `docs/spec/openapi-v0.json`: `POST /api/v0/pedidos-compra/{pedido_id}/recepciones`.
