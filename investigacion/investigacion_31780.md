# Investigación — Caracas, Elias (Legajo 31780)

> Nota: legajo verificado contra lo que me diste en esta conversación. El README del equipo tiene cargado el legajo 34575 para vos — revisá cuál es el correcto antes de entregar y, si está mal en el README, corregilo también ahí.

## Parte A — JS asincrónico + fetch + SPA

- Preguntas guía 1, 2, 3 (respuestas en MIS palabras):
  - [COMPLETAR] ¿Qué significa que fetch sea asincrónico? ¿Qué pasaría con la página si no lo fuera?
  - [COMPLETAR] ¿Por qué `respuesta.json()` también devuelve una promesa?
  - [COMPLETAR] ¿Qué relación hay entre una SPA y fetch? ¿Por qué la SPA "necesita" pedir datos así?
- Búsquedas (mínimo 2, con fuente y qué entendiste):
  - [COMPLETAR] ¿Qué es una SPA y en qué se diferencia de una MPA? — fuente:
  - [COMPLETAR] ¿Qué es una promesa y qué problema resuelve? — fuente:
  - [COMPLETAR] ¿Por qué fetch devuelve una promesa y no el dato directo? — fuente:
  - [COMPLETAR] ¿Qué diferencia hay entre XMLHttpRequest y fetch? — fuente:
- Evidencia de la actividad guiada:
  - Los tres fetch (básico, async/await, manejo de error 404) se corrieron de verdad contra `jsonplaceholder.typicode.com` desde Node — ver la sesión de terminal. **Correlo vos también en la consola del navegador (F12) y sacá la captura real**, la consigna pide específicamente eso, no la terminal.
  - Bonus: `investigacion/bonus-fetch-posts.html` — HTML con botón que lista los primeros 5 títulos. Abrilo en el navegador, apretá el botón y sacá la captura (`investigacion/captura-bonus-fetch.png`).

## Parte B — React + TypeScript + Vite

- Preguntas guía 1, 2, 3:
  - [COMPLETAR] ¿Qué relación ves entre "separar datos de la vista" (taller del 14/09) y el estado de React?
  - [COMPLETAR] ¿Por qué `interface IncidenciaProps` evita errores? ¿Dónde "vive" esa verificación?
  - [COMPLETAR] ¿Qué hace Vite que antes hacías a mano?
- Búsquedas (mínimo 2, con fuente y qué entendiste):
  - [COMPLETAR] ¿Qué es un componente en React? — fuente:
  - [COMPLETAR] ¿Qué es JSX? — fuente:
  - [COMPLETAR] ¿Qué es el estado (useState)? — fuente:
  - [COMPLETAR] ¿Qué son las props? — fuente:
- Evidencia:
  - Scaffold real en `investigacion/mi-primera-spa/` (Vite + React + TS, `npm create vite -- --template react-ts`, `npm install` sin errores).
  - `src/Incidencia.tsx`: componente con props tipadas (`IncidenciaProps { maquina: string; descripcion: string }`).
  - `src/App.tsx`: importa `Incidencia` y renderiza 3 incidencias con datos mock, más un `useState` que cuenta incidencias cargadas.
  - `npx tsc -p tsconfig.app.json --noEmit` corre limpio (0 errores) — ver `investigacion/evidencia-texto/`.
  - Error de tipos a propósito: se cambió `maquina={incidencia.maquina}` por `maquina={123}` y el compilador tiró `src/App.tsx(21,11): error TS2322: Type 'number' is not assignable to type 'string'.` (texto real en `investigacion/evidencia-texto/error-tipos-tsc.txt`). Se revirtió después.
  - **Server corriendo en `http://localhost:5173/` — abrilo vos y sacá 3 capturas**: el scaffold andando, tu componente Incidencia renderizado, y el error de tipos en el editor (podés reproducirlo: cambiá de nuevo `maquina={incidencia.maquina}` por `maquina={123}` en `src/App.tsx`, mirá el subrayado rojo en el editor, y volvé a dejarlo como estaba).

## Parte C — Contrato OpenAPI + Prism

- Preguntas guía 1, 2, 3:
  - [COMPLETAR] ¿Por qué conviene definir el contrato antes de codificar? ¿Qué desastre evita?
  - [COMPLETAR] ¿Cómo ayuda un mock server a que frontend y backend trabajen en paralelo?
  - [COMPLETAR] ¿Qué relación hay entre el contrato OpenAPI y las RN que documentamos en M1?
- Búsquedas (mínimo 2, con fuente y qué entendiste):
  - [COMPLETAR] ¿Qué es un contrato de API? — fuente:
  - [COMPLETAR] ¿Qué es un mock server? — fuente:
  - [COMPLETAR] ¿OpenAPI y Swagger son lo mismo? — fuente:
  - [COMPLETAR] ¿Qué es un `$ref`? — fuente:
- Evidencia:
  - Contrato usado: `investigacion/actividad-prism/contrato_ejemplo_openapi.yaml` (el de la cátedra, OpenAPI 3.1, endpoints `/incidencias` y `/repuestos`).
  - Prism instalado y corriendo de verdad: `prism mock investigacion/actividad-prism/contrato_ejemplo_openapi.yaml`, escuchando en `http://127.0.0.1:4010` (log real en `investigacion/evidencia-texto/prism-terminal-output.txt`).
  - `curl http://127.0.0.1:4010/repuestos` y `curl http://127.0.0.1:4010/incidencias` devolvieron datos mockeados reales (ver `investigacion/evidencia-texto/prism-repuestos.json` y `prism-incidencias.json`).
  - **Sacá vos la captura del `prism mock` corriendo en tu propia terminal y del curl/petición al mock** (podés dejar el server prendido y repetir los dos `curl` de arriba, o abrir las URLs directo en el navegador).

## Reflexión (máx. 5 líneas)

- [COMPLETAR] ¿Qué fue lo que más te costó y cómo lo destrabaste? (Esto tiene que ser tuyo — es la parte que más pesa en el nivel D de la rúbrica: conectar la investigación con tu CU del TCI, que es reportar incidencia.)
