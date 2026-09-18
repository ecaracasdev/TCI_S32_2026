# ADR: alcance de casos de uso del núcleo y lugar de "Registrar un repuesto"

- **Estado:** Propuesto
- **Fecha:** 2026-09-18
- **Autor:** Elias Caracas
- **Decisores:** Elias Caracas, Martín Carrasco y Nicolás Pieroni (a validar en la reunión de equipo)

## Contexto

El cronograma (`docs/cronograma_alumnos.md`, sección 5) define el alcance de un equipo núcleo de 3 integrantes:

- Registrar uso de repuesto en reparación (RN-01, RN-02, RN-06).
- Cargar stock recibido con ubicación (RN-08).
- Reportar incidencia con QR de máquina.
- Autenticación con 3 roles.

La sección 6 pide que cada integrante sea dueño de al menos un caso de uso completo, desde la especificación hasta el test.

Hoy solo CUN-01 (registrar uso de repuesto) está documentado en `main`. El caso de uso "Registrar un repuesto", numerado CUN-02 en esos PR (numeración que esta propuesta cambia), apareció en el PR #30 y en la rama de T08. No figura en el alcance del cronograma para ningún tamaño de equipo, y el dominio no describe el alta de repuestos como un proceso.

## Decisión propuesta

1. El núcleo queda formado por tres casos de uso:

| CU | Actor | Reglas | Pantalla |
| --- | --- | --- | --- |
| CUN-01 Registrar uso de repuesto en reparación | Empleado de mantenimiento | RN-01, RN-02, RN-06 | Issue #26 |
| CUN-02 Cargar stock recibido con ubicación | Encargado de mantenimiento (puede delegar) | RN-08 | Issue #27 |
| CUN-03 Reportar incidencia con QR de máquina | Operario de máquina | El cronograma no cita ninguna | Maquetado hecho |

2. La autenticación usa 3 roles: operario, empleado de mantenimiento y encargado. Son los que tienen un caso de uso propio en el núcleo.
3. Dueños propuestos, uno por caso de uso: Martín en CUN-01, Nicolás en CUN-02 y Elias en CUN-03.
4. "Registrar un repuesto" queda **fuera del núcleo**. Se renumera como CUN-04 y su documento se sube en un PR aparte, marcado como fuera del núcleo.
5. Los repuestos y las máquinas del catálogo se precargan con datos de prueba (seed) durante M2 a M5: entre 5 y 10 repuestos y 2 o 3 máquinas.
6. Si sobra tiempo después de M5, se evalúa implementar CUN-04.

## Justificación

- El cronograma no lo incluye y el equipo es de 3.
- El dominio no dice quién crea el catálogo. Asignarlo al encargado es una suposición.
- CUN-01 y la carga de stock necesitan que el repuesto ya exista. Los datos precargados lo resuelven sin un caso de uso adicional.
- Choque con RN-02: un repuesto recién registrado tiene stock 0 y umbral mínimo mayor o igual a 0, por lo que `stock disponible ≤ umbral` es verdadero desde el alta. Cada registro dispararía una alerta y la entrada en la lista de compras. Con el modelo de T04 que crea un pedido automático al llegar al umbral, también crearía un pedido. El caso de uso de registrar un repuesto, tal como está escrito en el PR #30, no contempla este caso.

## Alternativas consideradas

### Incluir "Registrar un repuesto" en el núcleo

Agrega una pantalla, endpoints y tests a un equipo de 3 sin que la cátedra lo pida. Se descarta salvo que sobre tiempo después de M5.

### No definir nada

Queda sin resolver qué pasa cuando se escanea un código que no está en el catálogo, y el alcance de cada integrante sigue ambiguo.

## Consecuencias

- Hay que mantener un seed de datos de prueba coherente con los tres casos de uso.
- Al escanear un código inexistente, el sistema lo rechaza con un mensaje claro. Esto debe quedar escrito en CUN-01 y CUN-02.
- Hay que renumerar el documento de "Registrar un repuesto" en el PR #30 y en la rama de T08.
- El CU de reportar incidencia y el de cargar stock todavía no están escritos. El contrato OpenAPI v0 depende de ellos.

## Preguntas abiertas para la reunión

- ¿Se acepta que un código inexistente se rechace en lugar de permitir crearlo en el momento?
- ¿Los 3 roles del auth son operario, empleado de mantenimiento y encargado?
- ¿Se acepta renumerar "Registrar un repuesto" como CUN-04?
- ¿Se acepta la asignación de dueños por caso de uso?
