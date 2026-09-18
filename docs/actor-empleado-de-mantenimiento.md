# Actor: empleado de mantenimiento

- **Tipo:** Rol humano del negocio.
- **Estado:** Primera versión pendiente de validación.

## Descripción

El empleado de mantenimiento es la persona que interviene sobre las máquinas cuando se informa una incidencia o se programa una tarea de mantenimiento. Es quien realiza el trabajo operativo y necesita consultar los repuestos disponibles para poder resolver una reparación.

## Qué debe hacer

1. Consultar las incidencias pendientes de atención.
2. Revisar la máquina involucrada y la descripción del problema.
3. Analizar la reparación que debe realizarse.
4. Buscar el repuesto necesario por código, nombre, descripción o código QR.
5. Verificar la cantidad disponible y su ubicación.
6. Utilizar el repuesto durante la reparación cuando corresponda.
7. Registrar la cantidad efectivamente utilizada.
8. Informar el resultado de la reparación o dejarla pendiente si falta un repuesto.

## Responsabilidad dentro del negocio

Su responsabilidad es ejecutar y registrar las tareas operativas de mantenimiento. Cada consumo debe quedar relacionado con la reparación correspondiente para conservar la trazabilidad.

## Información que necesita consultar

- Incidencias y reparaciones asignadas o disponibles.
- Máquinas y detalles de sus incidencias.
- Repuestos, cantidades y ubicaciones.
- Historial de consumos relacionados con una reparación.

## Acciones que no forman parte de su responsabilidad

- Autorizar la liberación de una reserva.
- Aprobar compras urgentes.
- Eliminar repuestos o movimientos históricos.
- Modificar directamente el stock sin una operación de entrada, consumo o reserva.

## Casos de uso relacionados

- Registrar uso de repuesto en una reparación.
- Consultar repuesto y disponibilidad.
- Consultar una incidencia o reparación.

## Vistas necesarias

La vista principal debería permitir consultar la reparación, buscar o escanear el repuesto, ingresar la cantidad utilizada y confirmar el consumo (vista mobile first).

## Decisiones pendientes

- Definir si se pueden quitar repuesto funcional de una máquina funcional.
- Definir quién registra el cierre formal de la reparación.
