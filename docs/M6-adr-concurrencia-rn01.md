# ADR M6: concurrencia del descuento de stock (RN-01)

- **Estado:** Propuesto
- **Fecha:** 2026-11-19
- **Decisores:** Elias Caracas, Martin Carrasco y Nicolás Pieroni
- **Relacionado:** `docs/dominio/dominio.md` (sección 7, hueco 2), `docs/caso-de-uso.md` (CUN-01), issue #112

## Contexto

RN-01 exige que usar un repuesto descuente su stock físico y que el resultado nunca quede negativo. El dominio deja abierto qué pasa si dos empleados descuentan la última unidad al mismo tiempo, y pide resolverlo con un ADR. Las opciones que menciona son una restricción `CHECK` en la base, `SELECT ... FOR UPDATE` o versionado optimista.

El problema aparece cuando el servicio primero **lee** el stock, decide en Python si alcanza y después **escribe** el nuevo valor. Entre la lectura y la escritura otra solicitud puede leer el mismo valor, y las dos descuentan creyendo que alcanza.

## Decisión

El descuento se hace con **una única sentencia condicionada** en la base, sin lectura previa que decida:

```sql
UPDATE repuestos_x_ubicaciones
   SET cantidad_fisica = cantidad_fisica - :cantidad
 WHERE repuesto_id = :repuesto AND ubicacion_id = :ubicacion
   AND cantidad_fisica - cantidad_reservada >= :cantidad
```

- Si la condición se cumple, la fila se actualiza (`rowcount = 1`) y el uso se registra en la misma transacción.
- Si no se cumple, no se actualiza ninguna fila (`rowcount = 0`) y la API responde `409 stock_insuficiente` sin modificar nada.
- La condición compara contra el **disponible** (físico − reservado), no solo contra el físico, para no usar unidades reservadas para otra tarea (RN-05).
- Como respaldo, las restricciones `CHECK` existentes impiden en cualquier caso stock físico negativo y reservado mayor que el físico.

Es la misma técnica que ya usan las reservas (`POST /reservas`, `/ejecucion` y `/liberacion`).

## Por qué funciona con dos usos simultáneos

La base evalúa la condición y actualiza la fila en una sola operación atómica, con la fila bloqueada durante la escritura. Si dos usos compiten por las últimas unidades, el segundo espera a que el primero termine y vuelve a evaluar la condición sobre el valor ya descontado: no se cumple y no actualiza. En PostgreSQL esto ocurre con el nivel de aislamiento por defecto (`READ COMMITTED`); en SQLite, que admite un solo escritor a la vez, las escrituras se serializan.

## Alternativas consideradas

- **Solo la restricción `CHECK`:** impide el stock negativo, pero el segundo uso falla con un error de integridad (un `500`) en lugar de un rechazo de negocio claro, y no protege lo reservado mientras el físico siga siendo positivo.
- **`SELECT ... FOR UPDATE`:** también es correcto, pero necesita dos sentencias y una transacción explícita, y SQLite no lo soporta, así que los tests no lo cubrirían igual que en producción.
- **Versionado optimista:** agrega una columna de versión y reintentos del lado de la aplicación. Es más código para el mismo resultado en una sola fila.

## Verificación

- `tests/test_reparaciones.py` comprueba que un uso mayor al disponible responde `409` sin cambiar el stock, que lo reservado no se usa y que el disponible exacto sí alcanza. Si se quita la condición de la sentencia, o se compara solo contra el físico, esos tests fallan.
- Se probó contra PostgreSQL 16 en Docker: un uso dentro del disponible descontó el stock y un pedido mayor respondió `409` sin cambios.

No se verificó una carrera real entre dos solicitudes simultáneas: la garantía viene de la atomicidad de la sentencia en la base, no de un test de concurrencia.

## Consecuencias

- El rechazo por falta de stock es siempre un `409` con un mensaje claro, también bajo concurrencia.
- Cada uso descuenta de una sola ubicación: la indicada o la de mayor disponible. Si ninguna alcanza sola, se rechaza aunque la suma de todas alcance. Repartir un uso entre ubicaciones queda pendiente.
