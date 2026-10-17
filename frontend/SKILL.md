# Skill de Frontend — TCI

Convenciones obligatorias para diseñar e implementar funcionalidades de frontend en este proyecto.

## Stack y estructura

- Usar Angular 21 y la arquitectura standalone existente.
- Ubicar cada funcionalidad en `src/app/features/<feature>/`. Mantener juntos los elementos propios de la feature (páginas, componentes, modelos, configuración y acceso a datos) con una organización clara y consistente.
- Centralizar los textos/configuración de cada feature en un archivo `*_CONFIG` cuando corresponda; evitar duplicar etiquetas y mensajes en plantillas.
- Usar Signals e `inject()` para el estado y la inyección de dependencias. Para control de flujo en plantillas, usar `@if` y `@for`.

## Servicios reales y mock

- Cada feature consume un contrato de servicio. Debe tener una implementación real conectada a la API/OpenAPI y una implementación `Mock<Recurso>Service` que cumpla el mismo contrato.
- Seleccionar la implementación mediante la configuración de entorno, usando `environment.useMockData`; las páginas no deben contener fixtures ni hacer peticiones HTTP directamente.
- Los fixtures se guardan en `public/mock/` y respetan los contratos de `docs/spec/openapi-v0.json`.
- Con `useMockData=true`, las vistas deben poder recorrerse sin iniciar sesión. Este acceso directo existe solo para el modo mock; no desactivar ni debilitar la autenticación del modo real.
- Identificar como demostración los resultados mock y no afirmar que se guardaron en el backend o que se enviaron notificaciones reales.

## Componentes y estilos

- Reutilizar los componentes de `src/app/shared/` antes de crear otros. Si una vista necesita una pieza reusable que todavía no existe, agregarla a `shared` y documentarla en la entrega.
- Usar variables visuales `--ui-*` en `src/styles.css`. Si la rama base todavía no las define, establecer allí los tokens necesarios antes de usarlos. No introducir colores, tipografías ni estilos compartidos duplicados como valores aislados.
- Mantener accesibilidad en formularios, navegación, acciones y estados visibles.
- Todo el texto de interfaz se escribe en español.

## Diseño adaptable

- Diseñar mobile-first y contemplar teléfono, tablet y escritorio.
- En colecciones, usar tablas en escritorio y tarjetas en tablet y teléfono. Formularios y detalles deben adaptar su distribución y controles a los tres tamaños.
- Incluir los estados de carga, error y vacío que correspondan al flujo.

## Validación de entrega

- El frontend debe compilar con `npm run build` desde `frontend/`.
- Si el alcance toca una decisión aún no definida en el dominio o en la API, dejarla explícita y no inventar comportamiento.
