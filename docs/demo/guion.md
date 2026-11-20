# Guion de la demo (M6)

Duración estimada: 15 minutos. Cada paso dice qué hacer, qué se tiene que ver y qué decir. Los números (cantidades, stock) corresponden a los datos recién cargados con `crear-dummy-db`.

## Antes de presentar

1. Levantar el sistema y cargar los datos de prueba: pasos 1 a 5 de [`levantar.md`](levantar.md). Si ya se hicieron ensayos, volver a los datos iniciales para que los números coincidan:

   ```bash
   docker compose exec backend uv run --no-dev crear-dummy-db --recreate --si
   ```

2. Abrir dos ventanas, lado a lado:
   - **Navegador** en http://localhost:8080.
   - **Terminal** en la raíz del repo, con los tokens y el repuesto de la demo listos. Si recargaste los datos, recalculá estas variables, porque los repuestos cambian de id:

     ```bash
     API=http://localhost:8300
     token() { curl -s -X POST $API/auth/token -d "username=$1@test&password=test&grant_type=password" | jq -r .access_token; }
     EMP=$(token empleado); ENC=$(token encargado); OPE=$(token operario)
     REP=$(curl -s $API/api/v0/repuestos/codigo/REP-00087 -H "Authorization: Bearer $EMP" | jq .id)
     UBI=$(curl -s $API/api/v0/repuestos/$REP -H "Authorization: Bearer $EMP" | jq '.stock[0].ubicacion_id')
     echo "repuesto $REP, ubicación $UBI"
     ```

3. Si vas a mostrar las tablas, dejá abierta en DBeaver la conexión a `tci` (paso 6 de `levantar.md`).

Usuarios: `operario@test`, `empleado@test`, `encargado@test` y `gerencia@test`. Contraseña de todos: `test`.

## Qué se ve

Cada rol ve en el menú solo lo que puede usar, y todo lo que aparece funciona contra el backend real:

| Rol | Menú |
| --- | --- |
| Operario | Inicio, Reportar incidencia, Incidencias |
| Empleado | Inicio, Incidencias, Registrar uso, Máquinas, Repuestos, Ubicaciones, Reposición, Compras |
| Encargado y gerencia | Inicio, Incidencias, Máquinas, Repuestos, Ubicaciones, Reposición, Compras, Pedidos de compra |

En **Pedidos de compra**, el encargado de mantenimiento puede gestionar los pedidos y gerencia puede consultarlos, sin aprobarlos ni cancelarlos.

## 1. Presentación (30 segundos)

> "Es el sistema de stock y mantenimiento de la planta: Angular 21 en el front, FastAPI en el back y PostgreSQL como base, todo levantado con `docker compose`. Vamos a mostrar el ciclo completo de una incidencia, desde que el operario la reporta hasta que el empleado la resuelve registrando los repuestos que usó (CUN-01), el stock por ubicación, las reservas con sus reglas de negocio, los pedidos de compra y cómo se controlan los permisos por rol."

## 2. El operario reporta una incidencia (2 minutos)

1. Entrar con `operario@test`. El menú muestra **Inicio, Reportar incidencia e Incidencias**. En Inicio aparece la tarjeta "Incidencias recientes".
2. Ir a **Reportar incidencia**:
   - Tocar **Escanear QR**: simula el escaneo y completa el código de una máquina (`F-02`, `B-04` o `C-01`).
   - Descripción: `Pierde presión al arrancar.`
   - Turno: dejar el que propone según la hora, o elegir otro. Las fotos son opcionales.
   - Tocar **Reportar**. Aparece el aviso **"Incidencia reportada"** y el formulario se limpia.
3. Probar un código inexistente: escribir `X-99` en el código y reportar. Aparece el aviso de error con "No existe una máquina con ese código".
4. Ir a **Incidencias**: la recién reportada aparece **primera**, en estado reportada. Entrar a **Ver detalle**.

> "El operario reporta desde la planta, con el QR de la máquina y fotos opcionales. La incidencia queda a nombre de quien inició sesión y en estado reportada. El operario también puede consultar las incidencias para seguir sus reportes."

## 3. El empleado resuelve la incidencia: CUN-01 (3 minutos)

1. Cerrar sesión y entrar con `empleado@test`. En **Inicio**, la incidencia recién reportada aparece en "Incidencias recientes". El menú tiene **Registrar uso** pero no **Reportar incidencia** (si se escribe a mano `http://localhost:8080/incidencias/nueva`, vuelve a Inicio).
2. Ir a **Incidencias**, abrir la recién reportada (**Ver detalle**) y tocar **Tomar incidencia**. Aparece el aviso **"Incidencia tomada"** y se abre **Registrar uso** con el número de reparación ya cargado.

> "El empleado toma la incidencia: se crea la reparación a su nombre y la incidencia pasa a En reparación. Es la precondición del CUN-01."

3. En **Código del repuesto** escribir `REP-00106` y tocar **Buscar**: muestra *Sensor de temperatura PT100, disponible 5, mínimo 3*.
4. Cantidad `2` → **Registrar uso**. Aparecen **"Uso registrado"** y **"Alerta de stock mínimo"**, y el disponible pasa a **3**.

> "Registrar el uso descuenta del stock físico (RN-01), deja el movimiento de consumo para la trazabilidad y, como quedó bajo el mínimo, el repuesto entra en las alertas (RN-02)."

5. Cantidad `5` → **Registrar uso**. Aparece el error *"No hay stock disponible suficiente de REP-00106: se piden 5 y hay 3 disponibles"*. El stock no cambia.

> "Si no alcanza, se rechaza sin tocar nada. Quedan 5 sensores en el estante, pero 2 están reservados para un mantenimiento planificado, así que solo hay 3 disponibles: lo reservado no se puede usar (RN-05). Y como el control lo hace la base en una sola sentencia, dos empleados no pueden llevarse la última unidad a la vez: está en el ADR de concurrencia."

6. Tocar **← Volver a la incidencia**: la sección **Reparación** muestra el repuesto usado. En **Finalizar reparación** escribir `Se reemplazaron los dos sensores de temperatura.` y tocar **Finalizar y resolver**. Aparece **"Incidencia resuelta"**: el estado pasa a **Resuelta**, la reparación a **Completada** y queda el informe.
7. Para cerrar el recorrido, entrar con `encargado@test` y abrir la misma incidencia: ve la reparación y el informe, sin botones. Con `operario@test` ve su incidencia **Resuelta**.

> "Ese es el ciclo completo: el operario reporta, el empleado toma, registra los repuestos y resuelve, y todos ven el resultado según su rol."

## 4. Catálogo de máquinas (1 minuto)

Con el **empleado**:

1. Ir a **Máquinas**: se ven 18 máquinas.
2. Entrar a **C-01**: caldera operativa, número de serie `CA-2018-001`.

> "El login emite un JWT. El front lo guarda y un interceptor lo agrega a cada pedido a la API."

3. Cerrar sesión y entrar con `encargado@test`. En **Máquinas** aparecen **Agregar máquinas** y **Nuevo tipo**, y en el detalle de C-01, **Editar máquina**.

> "El encargado es el único que da de alta y edita máquinas. El front oculta esas acciones a los demás, pero quien decide es el backend: valida el rol en cada pedido, leyéndolo de la base."

## 5. Repuestos y stock por ubicación (2 minutos)

Con el **empleado** (volver a entrar con `empleado@test`):

1. **Repuestos**: el inventario con 13 repuestos, con físico, reservado y disponible en cada fila. Escribir `rodamiento` y tocar **Buscar**.
2. Abrir **REP-00142, Rodamiento 6205-2RS**: aparece **Bajo mínimo** y la tabla de existencias por ubicación.

> "El stock disponible es el físico menos lo reservado, y es el número que decide si se puede usar o reservar un repuesto."

3. **Nuevo repuesto**: código `REP-00300`, nombre `Termostato de seguridad TS-90`, mínimo `2`. Guardar. Queda creado sin existencias.
4. Intentar crear otro con código `REP-00142`: la pantalla avisa que ya existe.

> "Un repuesto nuevo arranca sin stock: el stock entra por las recepciones de compra, no se escribe a mano."

## 6. Permisos por rol (1 minuto)

1. Entrar con `gerencia@test` y abrir **Repuestos**: puede consultar, pero no aparece **Nuevo repuesto** ni **Editar repuesto**.
2. En la terminal, lo mismo sin el front:

   ```bash
   curl -s $API/api/v0/repuestos -H "Authorization: Bearer $OPE" -w " %{http_code}\n"
   curl -s -o /dev/null -w "%{http_code}\n" $API/api/v0/repuestos
   ```

   Responde `403` con `"El usuario no tiene el rol requerido."` (el operario no accede al almacén) y después `401` sin token.

> "El front muestra a cada rol solo sus módulos, pero la seguridad la decide el backend: aunque alguien llame a la API sin pasar por el front, recibe 403, y sin token 401. La matriz de permisos está en `docs/actores.md` y es la misma en los dos lados."

## 7. Reservas: RN-05 y RN-10 (3 minutos)

Las reservas todavía no tienen pantalla: se muestran con la API desde la terminal. Para ver el efecto, dejar abierto en el navegador (como empleado) el detalle de **REP-00087, Filtro de aceite FO-18** (en **Repuestos**, escribir `filtro`, tocar **Buscar** y entrar con el nombre) y recargarlo después de cada paso.

**Antes:** físico 4, reservado 0, disponible 4.

```bash
curl -s $API/api/v0/repuestos/$REP -H "Authorization: Bearer $EMP" | jq '{codigo, stock_fisico_total, stock_reservado_total, stock_disponible_total}'
```

**a) Reservar 3 unidades para un mantenimiento preventivo:**

```bash
R=$(curl -s -X POST $API/api/v0/reservas -H "Authorization: Bearer $EMP" -H "Content-Type: application/json" \
  -d "{\"titulo\":\"Preventivo de la línea de envasado\",\"planificada_para\":\"2026-11-25T08:00:00Z\",\"items\":[{\"repuesto_id\":$REP,\"ubicacion_id\":$UBI,\"cantidad\":3}]}")
echo "$R" | jq '{id, estado, items: [.items[] | {cantidad, cantidad_consumida}]}'
ID=$(echo "$R" | jq .id); ITEM=$(echo "$R" | jq '.items[0].id')
```

Resultado: reserva `activa`. Al recargar el repuesto: físico 4, **reservado 3, disponible 1**.

> "Reservar no saca el repuesto del estante, pero lo aparta: deja de estar disponible para otra incidencia. Es la primera mitad de RN-05."

**b) Intentar reservar más de lo disponible:**

```bash
curl -s -X POST $API/api/v0/reservas -H "Authorization: Bearer $EMP" -H "Content-Type: application/json" \
  -d "{\"titulo\":\"Otra\",\"planificada_para\":\"2026-11-26T08:00:00Z\",\"items\":[{\"repuesto_id\":$REP,\"ubicacion_id\":$UBI,\"cantidad\":2}]}" -w " %{http_code}\n"
```

Resultado: `409 stock_insuficiente`. El stock no cambia.

> "El control se hace en la base con una sola sentencia condicionada: si dos personas reservan a la vez la última unidad, una de las dos recibe este 409. Y si una reserva tiene varias partidas y una no alcanza, no se reserva ninguna."

**c) El empleado intenta liberar la reserva:**

```bash
curl -s -X POST $API/api/v0/reservas/$ID/liberacion -H "Authorization: Bearer $EMP" -w " %{http_code}\n"
```

Resultado: `403`.

> "Liberar una reserva exige rol encargado: es la segunda mitad de RN-05."

**d) Se hace el mantenimiento y se usan 2 de las 3 unidades (RN-10):**

```bash
curl -s -X POST $API/api/v0/reservas/$ID/ejecucion -H "Authorization: Bearer $EMP" -H "Content-Type: application/json" \
  -d "{\"items\":[{\"item_reserva_id\":$ITEM,\"cantidad_consumida\":2}]}" | jq '{estado, items: [.items[] | {cantidad, cantidad_consumida}]}'
```

Resultado: reserva `ejecutada`. Al recargar el repuesto: **físico 2, reservado 0, disponible 2**.

> "Ejecutar descuenta del físico lo que se usó y libera lo que sobró, las dos cosas en la misma transacción. Si algo falla en el medio, no queda nada a medias: lo cubre un test que fuerza el fallo."

**e) El encargado libera una reserva que se cancela:**

```bash
ID2=$(curl -s -X POST $API/api/v0/reservas -H "Authorization: Bearer $EMP" -H "Content-Type: application/json" \
  -d "{\"titulo\":\"Se cancela\",\"planificada_para\":\"2026-11-27T08:00:00Z\",\"items\":[{\"repuesto_id\":$REP,\"ubicacion_id\":$UBI,\"cantidad\":1}]}" | jq .id)
curl -s -X POST $API/api/v0/reservas/$ID2/liberacion -H "Authorization: Bearer $ENC" | jq '{estado, autorizada_por_usuario_id}'
```

Resultado: `liberada`, con el encargado registrado como quien la autorizó.

## 8. Pedidos de compra: CUN-03 (2 minutos)

Los datos de prueba traen un solo pedido en "Pendiente de aprobación". Para mostrar también la cancelación, pasá antes un segundo pedido a ese estado desde la terminal (la revisión no tiene pantalla):

```bash
PED=$(curl -s "$API/api/v0/pedidos-compra?estado=pendiente_revision&limit=1" -H "Authorization: Bearer $ENC" | jq '.items[0].id')
curl -s -X POST $API/api/v0/pedidos-compra/$PED/revision -H "Authorization: Bearer $ENC" -H "Content-Type: application/json" -d '{}' | jq '{id, estado}'
```

Resultado: el pedido queda en `pendiente_aprobacion`.

1. Entrar con `encargado@test` e ir a **Pedidos de compra**: la lista muestra origen, urgencia y estado de cada pedido.
2. Abrir un pedido en **Pendiente de aprobación**, tocar **Aprobar pedido** y después **Sí, aprobar**. El estado pasa a **Confirmado**.
3. Abrir el otro pedido en **Pendiente de aprobación**, tocar **Cancelar pedido**, escribir el motivo (`El proveedor ya no fabrica la válvula.`) y tocar **Confirmar cancelación**. El estado pasa a **Cancelado** y el motivo queda registrado.
4. Cerrar sesión y entrar con `gerencia@test`: ve **Pedidos de compra** y el detalle de cada pedido, pero sin botones de acción.

> "El encargado aprueba o cancela los pedidos que esperan aprobación, siguiendo la máquina de estados del pedido. Gerencia solo consulta. Una acción sobre un pedido en otro estado se rechaza, y cancelar exige un motivo."

## 9. Todo quedó en PostgreSQL (1 minuto)

```bash
docker compose exec db psql -U tci -d tci -c "select tipo_movimiento, cantidad, variacion_fisica, variacion_reservada from movimientos_stock where item_reserva_id is not null order by id desc limit 5;"
```

Se ven, del más nuevo al más viejo: `liberacion` (-1 reservado), `reserva` (+1), `liberacion` (-1, lo que sobró de la ejecución), `consumo` (-2 físico y -2 reservado) y `reserva` (+3).

> "Cada cambio de stock queda como un movimiento que no se modifica: así se reconstruye la historia de cada repuesto (RN-06). La base es PostgreSQL 16, levantada por el compose. Sin Docker y en los tests usamos SQLite, y la decisión con sus pruebas está en el ADR `docs/M6-adr-sqlite-o-postgres.md`."

## 10. Contrato y tests (1 minuto)

1. Abrir http://localhost:8300/docs: el Swagger con las rutas implementadas, incluidas incidencias, reservas y alertas de stock.

> "El contrato v0 se definió primero, en M2, y el backend lo va implementando: lo que ya está coincide con el contrato en rutas, parámetros y esquemas."

No intentar ejecutar desde el Swagger las rutas protegidas: no tiene botón para cargar el token. Para eso está la terminal.

2. En la terminal, los tests de reservas:

   ```bash
   cd backend && uv run pytest tests/test_reservas.py -v
   ```

   Se ven los 7 tests en verde, con la regla en el nombre (`test_rn05_...`, `test_rn10_...`). Los del CUN-01 están en `tests/test_reparaciones.py` (`test_rn01_...`). Los tests de CUN-03 están en `tests/test_pedidos_compra.py`. La suite completa del backend corre con `uv run pytest -q`.

> "Cada uno de estos tests comprueba reglas y errores esperados. Las verificaciones manuales de la demo se realizan con Docker y PostgreSQL."

## Preguntas probables

**"¿Y los pedidos de compra?"**

El sistema permite consultar pedidos, asignar responsables, revisar, aprobar y cancelar pedidos de compra. La aprobación los deja en estado `confirmado`; la cancelación requiere un motivo y los deja en estado `cancelado`. La recepción de mercadería es otro caso de uso (CUN-02) y no forma parte de esta demostración.

**"¿Qué pasa si falta stock para la reparación?"**

Se rechaza el uso con el faltante. El CUN-01 prevé ofrecer un pedido de compra (RN-03) y dejar la incidencia "Pendiente de repuesto": eso depende de la integración de ese flujo.

**"¿Por qué las reservas no tienen pantalla?"**

Priorizamos la regla de negocio con sus tests (RN-05 y RN-10), que era lo que faltaba. La pantalla queda pendiente.

**"¿Qué pasa si dos empleados usan o reservan la última unidad a la vez?"**

El descuento y la reserva se hacen con un `UPDATE ... WHERE disponible >= cantidad` en una sola sentencia: solo una de las dos actualiza la fila y la otra recibe `409`. Además la base tiene restricciones `CHECK`: el stock físico nunca queda negativo y lo reservado nunca supera al físico. La decisión está en `docs/M6-adr-concurrencia-rn01.md`.

**"¿Los tests corren contra PostgreSQL?"**

No: corren contra SQLite. La aplicación corre en PostgreSQL, y las reservas y las incidencias se probaron a mano contra PostgreSQL. Pasar la suite a PostgreSQL implica reescribir los tests que usan `sqlite3` directo, y está anotado como pendiente en el ADR.

**"¿Por qué no hay migraciones con Alembic?"**

El esquema se crea al iniciar con `create_all`. Alembic es lo primero que habría que agregar antes de producción, y así está escrito en el ADR.
