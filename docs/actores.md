# Actores del dominio

> T08. Formaliza los actores ya descriptos en `docs/dominio/dominio.md` (sección 3), agregando permisos y la relación con las pantallas construidas hasta ahora.

## Los 4 roles

| Rol | Qué hace | Acceso |
| --- | --- | --- |
| **Operario de máquina** | Reporta incidencias y solicita reparaciones (fotos + QR de la máquina), en cualquier turno. | Alta de incidencias. Sin acceso a stock ni a compras. |
| **Empleado de mantenimiento** | Ingresa repuestos al almacén (escaneo), consulta existencia, registra el uso de repuestos en una reparación. | Lectura y escritura sobre repuestos/stock y líneas de uso. Sin acceso a aprobar pedidos ni a gestionar usuarios. |
| **Encargado de mantenimiento** | Mantiene la lista de compras, carga el stock recibido (o delega y supervisa), autoriza la liberación de reservas, revisa y aprueba/cancela pedidos de compra. | Lectura y escritura sobre pedidos de compra y recepciones. Única autoridad para liberar una reserva (RN-05). |
| **Gerencia / Administración** | Solo lectura: tableros de seguimiento y notificaciones de pedidos de compra. | Decisión de cátedra (dominio.md §7): "Gerencia de producción" y "Personal administrativo" se fusionan en este único rol de consulta. |

## Permisos por rol y pantalla construida

| Pantalla | Operario | Empleado de mantenimiento | Encargado | Gerencia/Administración |
| --- | --- | --- | --- | --- |
| Reportar incidencia (T16) | Alta | — | — | — |
| Registrar uso de repuesto (T17, CUN-01) | — | Alta | — | — |
| Consulta de incidencias (T13) | Lectura | Lectura | Lectura | Lectura |
| Registrar un repuesto (T28, CUN-04) | — | — | Alta | — |
| Consulta de repuestos / stock (T12) | — | Lectura | Lectura | Lectura |
| Reposición de repuestos (T14) | — | Lectura | Lectura | Lectura |
| Generar pedido de compra (T15) | — | Alta (reporta faltante) | Lectura/gestión | Lectura |
| Consultar pedidos de compra (T18) | — | — | Lectura | Lectura |
| Consultar máquinas (T19) | — | Lectura | Lectura | Lectura |
| Cargar stock recibido con ubicación (RN-08, pendiente — issue #27) | — | — | Alta (o delega) | — |

La tabla de permisos es una propuesta para validar: hoy el frontend no tiene autenticación real ni estas restricciones implementadas (todas las pantallas se navegan sin login en modo mock, ver `frontend/SKILL.md`), así que esto queda como la referencia a implementar cuando se conecte la autenticación real (M5).

## Permisos de la API de repuestos y ubicaciones (T28)

El backend verifica estos roles en cada solicitud, leyéndolos de la base (no del token). Sin token responde `401`; con un rol sin permiso, `403`.

| Operación | Operario | Empleado de mantenimiento | Encargado | Gerencia/Administración |
| --- | --- | --- | --- | --- |
| Listar, buscar y consultar repuestos (`GET /repuestos`, `/repuestos/{id}`, `/repuestos/codigo/{codigo}`) | — | Sí | Sí | Sí |
| Crear repuestos (`POST /repuestos`) | — | — | Sí | — |
| Actualizar repuestos (`PATCH /repuestos/{id}`) | — | Sí | Sí | — |
| Listar ubicaciones (`GET /ubicaciones`) | — | Sí | Sí | Sí |
| Crear ubicaciones (`POST /ubicaciones`) | — | Sí | Sí | — |

El encargado da de alta repuestos en el catálogo. El empleado y el encargado pueden actualizar repuestos y gestionar ubicaciones; el ingreso de unidades corresponde a la recepción (RN-08). Gerencia solo consulta y el operario no accede al almacén.

## Permisos de la API de incidencias (T29)

Acordado con el equipo el 19/11: solo el operario reporta; todos los roles consultan, el operario incluido, para seguir sus reportes. El frontend muestra "Reportar incidencia" solo al operario.

| Operación | Operario | Empleado de mantenimiento | Encargado | Gerencia/Administración |
| --- | --- | --- | --- | --- |
| Reportar una incidencia (`POST /incidencias`) | Sí | — | — | — |
| Listar y consultar incidencias (`GET /incidencias`, `/incidencias/{id}`) | Sí | Sí | Sí | Sí |

## Permisos de la API de reservas (RN-05 y RN-10)

| Operación | Operario | Empleado de mantenimiento | Encargado | Gerencia/Administración |
| --- | --- | --- | --- | --- |
| Listar y consultar reservas (`GET /reservas`, `/reservas/{id}`) | — | Sí | Sí | Sí |
| Crear una reserva (`POST /reservas`) | — | Sí | Sí | — |
| Ejecutar una reserva (`POST /reservas/{id}/ejecucion`) | — | Sí | Sí | — |
| Liberar una reserva (`POST /reservas/{id}/liberacion`) | — | — | Sí | — |

Solo el encargado libera una reserva (RN-05) y queda registrado como quien la autorizó. El empleado crea y ejecuta las reservas porque es quien hace el mantenimiento. El aviso inmediato de la liberación depende del puerto de notificación (RN-09) y todavía no está implementado.

## Fuente

- `docs/dominio/dominio.md`, sección 3 (actores) y sección 7, decisión 1 (fusión de Gerencia y Administración).
- Issues cerradas de frontend (T11 a T20) para la columna de pantallas.
