# Actor: responsable de gestión y administración

- **Tipo:** Rol humano de consulta.
- **Estado:** Primera versión pendiente de validación.

## Descripción

El responsable de gestión y administración utiliza el sistema para obtener una visión general del funcionamiento de la planta. No participa normalmente en la reparación diaria, pero necesita consultar la información para supervisar resultados, detectar problemas y tomar decisiones.

## Qué debe hacer

1. Acceder a la información general del sistema (maquinas, repuestos, movimientos de repuestos).
2. Consultar el estado del stock y los repuestos críticos.
3. Revisar incidencias y reparaciones abiertas.
4. Consultar pedidos, recepciones y alertas importantes.
5. Filtrar la información por máquina, período, turno o estado cuando corresponda.
6. Utilizar tableros o reportes para analizar la operación.

## Responsabilidad dentro del negocio

Su responsabilidad es supervisar y analizar información. El rol no debe alterar las operaciones que realizan mantenimiento y supervisión, salvo que el equipo defina una responsabilidad adicional.

## Información que necesita consultar

- Indicadores de stock.
- Incidencias y reparaciones.
- Pedidos y compras urgentes.
- Consumos y movimientos relevantes.
- Informes de resolución.

## Acciones que no forman parte de su responsabilidad

- Registrar consumos.
- Modificar stock.
- Liberar reservas.
- Eliminar información histórica.
- Consultar directamente las tablas internas de la base de datos.

## Casos de uso relacionados

- Consultar repuesto y disponibilidad.
- Consultar incidencias y reparaciones.
- Consultar tableros e indicadores.

## Vistas necesarias

La vista principal debería ofrecer tableros, indicadores, filtros y reportes de consulta sin presentar operaciones de modificación que el rol no pueda realizar (backoffice responsive).

## Decisiones pendientes

- Definir si puede exportar reportes.
- Definir si recibe todas las notificaciones o solamente las urgentes.
- Definir si el rol puede realizar alguna modificación administrativa.
