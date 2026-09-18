# Actor: operador de máquina

- **Tipo:** Rol humano del negocio.
- **Estado:** Primera versión pendiente de validación.

## Descripción

El operador de máquina es la persona que trabaja directamente con los equipos de producción. Por su actividad cotidiana, es quien suele detectar primero una falla, un comportamiento extraño o una situación que puede interrumpir el funcionamiento normal de una máquina.

## Qué debe hacer

1. Detectar una anomalía o una necesidad de reparación.
2. Identificar la máquina involucrada, preferentemente mediante su código QR.
3. Describir de manera clara qué ocurrió y cuándo lo observó.
4. Adjuntar fotografías cuando puedan ayudar a comprender el problema.
5. Enviar la incidencia al área de mantenimiento.
6. Consultar, cuando corresponda, el estado de la incidencia informada.

## Responsabilidad dentro del negocio

Su responsabilidad es comunicar correctamente el problema observado. No debe diagnosticar técnicamente la falla ni decidir qué repuesto se utilizará.

## Información que necesita consultar

- Identificación de la máquina.
- Incidencias informadas por él.
- Estado de esas incidencias, si el equipo define que esa consulta estará disponible.

## Acciones que no forman parte de su responsabilidad

- Modificar el stock.
- Registrar consumos de repuestos.
- Aprobar reservas.
- Generar o aprobar pedidos de compra.
- Modificar la configuración general del sistema.

## Casos de uso relacionados

- Informar una incidencia de máquina.
- Consultar el estado de una incidencia, si se incorpora al alcance.

## Vistas necesarias

La vista principal debería permitir identificar la máquina, describir la incidencia, adjuntar fotografías y confirmar el envío del reporte.

## Decisiones pendientes
- Definir si puede reportar incidencias desde cualquier máquina o solamente desde las que tiene asignadas.
- Definir si una maquina puede tener pendientes varias revisiones o solo una activa a la vez.