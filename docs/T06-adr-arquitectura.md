# ADR T06: elección de arquitectura y stack tecnológico

- **Estado:** Propuesto
- **Fecha:** 2026-09-11
- **Decisores:** Elias Caracas, Martin Carrasco y Nicolás Pieroni

## Contexto

Antes de revisar el cronograma completo de la cátedra, el equipo había acordado utilizar Angular para el frontend y FastAPI para el backend. Esta decisión se tomó considerando la experiencia disponible, la organización esperada del proyecto y la intención de mantener una estructura clara desde el comienzo.

El cronograma propone React para el frontend y SQLModel para la capa de datos. En esta etapa no consideramos conveniente reemplazar el stack acordado por una indicación posterior, porque el cambio produciría retrabajo en la plantilla, en la estructura del proyecto y en las decisiones ya tomadas por el equipo.

La decisión queda sujeta a que las consignas evaluables de la cátedra no establezcan el uso obligatorio de una tecnología específica. Si existiera una incompatibilidad explícita, deberemos revisarla con el equipo y la cátedra.

## Decisión

Decidimos mantener la siguiente arquitectura y stack:

- **Frontend:** Angular 21 con TypeScript.
- **Backend:** FastAPI sobre Python.
- **Validación y contratos:** Pydantic mediante DTOs separados.
- **Persistencia:** SQLAlchemy como ORM.
- **Base de datos prevista:** PostgreSQL para el entorno objetivo.
- **Arquitectura:** organización modular y multicapa.

La arquitectura se dividirá en las siguientes responsabilidades:

1. **Presentación:** componentes, páginas y navegación del frontend.
2. **Routers o controladores:** recepción de solicitudes HTTP y devolución de respuestas.
3. **Servicios o casos de uso:** coordinación de la lógica de aplicación.
4. **Dominio:** reglas de negocio y conceptos propios del sistema.
5. **Persistencia:** repositorios y modelos SQLAlchemy.
6. **Infraestructura:** configuración, autenticación, base de datos y notificaciones.

## Justificación del frontend

Elegimos Angular porque, para el tamaño inicial de este proyecto y la forma de trabajo del equipo, ofrece una estructura más guiada y modular. La separación entre componentes, rutas, servicios, modelos y funcionalidades facilita que cada integrante trabaje sobre una parte concreta sin mezclar responsabilidades.

También valoramos que Angular incluya convenciones claras para organizar el proyecto, inyección de dependencias, enrutamiento y formularios. Esto permite mantener una estructura uniforme y facilita la incorporación de nuevos módulos a medida que crezca el sistema.

No afirmamos que Angular sea universalmente superior a React. La elección responde al contexto del equipo, a la estructura que ya comenzamos a construir y al costo de cambiar de tecnología en esta etapa.

## Justificación de SQLAlchemy y DTOs separados

Decidimos utilizar SQLAlchemy en lugar de SQLModel para mantener separados:

- El modelo de persistencia de la base de datos.
- El contrato semántico de la API.
- La lógica de aplicación.

Los DTOs representan los datos que una operación puede recibir o devolver. Los modelos SQLAlchemy representan la forma en que esos datos se almacenan. No necesariamente deben tener los mismos campos ni exponer la misma información.

Por ejemplo, una operación de actualización puede aceptar un DTO con únicamente `nombre`, `apellido` y `telefono`, mientras que el modelo de base de datos también puede contener `id`, fechas de auditoría, permisos, credenciales o relaciones internas.

La conversión explícita entre DTOs y modelos de persistencia agrega algo de código, pero evita acoplar el contrato público de la API con la estructura interna de la base de datos. También permite modificar el esquema interno sin cambiar automáticamente lo que recibe o ve el frontend.

## Alternativas consideradas

### React

React fue considerado porque aparece como tecnología propuesta para el frontend. Decidimos no adoptarlo en esta etapa debido a que el equipo ya había acordado Angular y comenzó a organizar la plantilla con sus convenciones. Cambiar ahora implicaría rehacer la estructura inicial y volver a evaluar librerías, navegación, formularios y organización de componentes.

### SQLModel

SQLModel fue considerado porque integra modelos compatibles con Pydantic y SQLAlchemy. Decidimos no adoptarlo porque preferimos que los modelos de persistencia y los DTOs tengan responsabilidades distintas. Esta separación resulta especialmente importante para operaciones parciales, como actualizar solamente algunos campos de un recurso.

## Consecuencias positivas

- Mantenemos el trabajo inicial y evitamos retrabajo inmediato.
- El frontend conserva una estructura modular y previsible.
- Los DTOs pueden diseñarse según cada operación de la API.
- Los modelos de base de datos no quedan expuestos directamente al frontend.
- La lógica de negocio puede probarse sin depender de la representación de persistencia.
- Las capas pueden evolucionar de forma más independiente.

## Consecuencias negativas y riesgos

- Debemos escribir y mantener mapeos entre DTOs y modelos SQLAlchemy.
- La arquitectura requiere disciplina para no colocar lógica de negocio en routers o componentes.
- Angular puede tener mayor estructura inicial que otras alternativas.
- El stack elegido no coincide completamente con las tecnologías propuestas en el cronograma.
- La aceptación de esta decisión debe confirmarse si la cátedra considera obligatorio utilizar React o SQLModel.

## Alcance de esta decisión

Este ADR define la orientación arquitectónica y la separación de responsabilidades. No define todavía:

- El diseño final de todas las entidades.
- Los endpoints definitivos.
- La implementación de autenticación.
- La estrategia completa de migraciones.
- La configuración final de despliegue.

Esas decisiones se documentarán en tareas o ADRs específicos cuando corresponda.
