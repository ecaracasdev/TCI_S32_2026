# CU: Registrar uso de repuesto en una reparación

## Identificación
- **ID**: CUN-01
- **Objetivo**: Descontar del stock los repuestos usados en una reparación, dejando registrada la trazabilidad de ese uso
- **Prioridad**: Alta
- **Actor principal**: Empleado de mantenimiento
- **Actores secundarios**: Sistema de notificación (correo), Encargados (reciben alerta si aplica)

## Precondiciones
- El empleado está autenticado con rol Empleado de mantenimiento
- Existe una incidencia en estado En reparación asociada a la máquina
- El repuesto existe en el sistema con un código QR

## Postcondiciones (éxito)
- El stock físico del repuesto quedó descontado en la cantidad usada
- Se creó una línea de uso vinculada a la reparación
- Se generó un movimiento de stock tipo consumo
- Si el stock disponible resultante quedó ≤ umbral mínimo se disparó la alerta y el repuesto entró en la lista de compras

## Escenario principal
1. El empleado escanea el código QR del repuesto
2. El sistema muestra nombre, descripción y stock disponible
3. El empleado ingresa la cantidad usada
4. El sistema valida stock físico − cantidad
5. El sistema descuenta el stock físico
6. El sistema registra la línea de uso asociada a la reparación/incidencia
7. El sistema evalúa el umbral mínimo y genera alerta si corresponde

## Escenario alternativo — falta de stock
Paso 4, si stock físico − cantidad < 0:
- El sistema rechaza la operación
- Informa al empleado el faltante
- Le ofrece generar un pedido de compra, derivando al CU "Generar pedido de compra"
- La reparación queda pendiente de ese repuesto

## Regla de negocio explícita
RN-01 — Descuento por uso. Usar un repuesto en una reparación descuenta del stock físico la cantidad de la línea de uso. El stock físico resultante debe ser ≥ 0: si no alcanza, el uso se rechaza.
