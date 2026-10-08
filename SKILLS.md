# Skill vigente

Esta nota conserva las convenciones base de Angular. Las reglas complementarias sobre ADA, Keycloak, mocks, SCSS y límites del agente se encuentran en la guía ampliada de Angular del proyecto.

---

# Angular — Convenciones de Aplicación

## Versión y sintaxis
- **Angular 21**. Sin sintaxis legacy bajo ninguna circunstancia.
- Signals API: `input()`, `output()`, `signal()`, `computed()`, `effect()`.
- No usar `@Input()` / `@Output()` decorators.
- No usar `ngOnChanges`. Usar `effect()` para reaccionar a cambios de inputs.
- Control flow moderno: `@if`, `@for`, `@empty`, `@let`. No usar `*ngIf`, `*ngFor`.
---
## Estructura de carpetas

```
src/
├── app/
│   ├── app.config.ts
│   ├── app.css
│   ├── app.html
│   ├── app.routes.ts
│   ├── app.ts
│   ├── core/
│   │   ├── models/          ← interfaces/types agrupados por dominio
│   │   │   └── commerce.models.ts
│   │   ├── services/        ← lógica de negocio y acceso a datos
│   │   │   └── api.service.ts
│   │   └── shared/          ← componentes de propósito general reutilizables
│   │       ├── header.component.ts
│   │       └── footer.component.ts
│   └── features/
│       └── [feature]/
│           ├── components/  ← sub-componentes all-in-one de la feature
│           ├── [feature].page.ts
│           ├── [feature].page.html
│           └── [feature].page.css
├── environments/
│   ├── environment.ts       ← activo (apunta a base, mock o prod)
│   ├── environment.base.ts
│   ├── environment.mock.ts
│   └── environment.prod.ts
├── styles.css               ← variables CSS globales + reset
└── main.ts
```

### Reglas de ubicación

| Qué | Dónde |
|---|---|
| Componente reutilizable entre features | `core/shared/` |
| Sub-componente exclusivo de una feature | `features/[feature]/components/` |
| Lógica de negocio / datos | `core/services/` |
| Interfaces y tipos | `core/models/[dominio].models.ts` |
| Página principal de una feature | `features/[feature]/[feature].page.ts` |

---

## Nomenclatura de archivos

Sufijo obligatorio según tipo:

| Tipo | Sufijo |
|---|---|
| Página (orquestadora de feature) | `.page.ts` |
| Componente | `.component.ts` |
| Servicio | `.service.ts` |
| Modelo | `.models.ts` |
| Pipe | `.pipe.ts` |
| Guard | `.guard.ts` |
| Resolver | `.resolver.ts` |

---

## Features — página + componentes

- Cada feature tiene **una página** (`[feature].page.ts`) que orquesta la lógica y el layout.
- La página delega secciones a **componentes all-in-one** en `components/`.
- Los componentes de feature son autocontenidos: template, estilos y lógica en un solo archivo cuando es posible.
- Objetivo: que cada archivo sea auditable de forma independiente con contexto mínimo.

## Textos fijos
- Cada Pagina que tiene textos modificables los tiene en un `"{{FEATURE_NAME}}_CONFIG"`, que contiene el texto para esa pagina.
- Al acceder a esa sección de texto se usa esa variable de configuración.

## Componentes Compartidos (Shared)
- Conviven en "@core/shared" y son componentes con lógica generica que tienen como objetivo poder reutilizarse.

---

## Modelos

- Preferir **interfaces** para DTOs y estructuras de datos simples.
- Usar **clases** solo cuando haya métodos con lógica no trivial (ej: formateo de fechas, cálculos derivados).
- Agrupar por dominio en un solo archivo: `commerce.models.ts`, `user.models.ts`, etc. No un archivo por modelo.
- La lógica sobre los datos va en el **service**, no en el modelo.

```typescript
// ✅ correcto
interface Product {
  id: string;
  name: string;
  price: number;
}

// ✅ clase solo si tiene lógica
class SaleTicket {
  constructor(public data: SaleTicketDto) {}
  get formattedDate(): string { ... }
}
```

---

## Servicios y estado

- La lógica de negocio vive en **services**. Los stores son excepcionales.
- Preferir no persistir estado del lado del cliente salvo necesidad explícita.
- Un service puede tener signals internos si necesita estado reactivo local.

---

## Estilos

- **Variables CSS obligatorias** en `styles.css` para colores, tipografías y espaciados clave.
- Usar nombres semánticos con prefijo `--ui-*` para los tokens visuales compartidos.
- Todo color, fuente o valor reutilizable debe ser una variable. No valores hardcodeados en componentes.
- Los componentes referencian variables del global, no definen sus propios colores base.
- **Mobile-first:** definir primero la presentación para pantallas pequeñas y ampliarla progresivamente con media queries `min-width`. No diseñar primero para escritorio y luego reducirlo para mobile.

```css
/* styles.css */
:root {
  --ui-background: #f9fafb;
  --ui-surface: #ffffff;
  --ui-text: #374151;
  --ui-text-muted: #6b7280;
  --ui-border: #e5e7eb;
  --ui-primary: #111827;
}
```
---

## Environments y mock
  - `environment.mock.ts` provee datos de prueba sin backend real.
  - Los datos mock viven en `public/mock/` (archivos JSON, imágenes, etc.).
  - Los services tienen una "factory" o método que carga datos mock cuando el environment lo indica.
  - Permite desarrollar y auditar la UI completamente desconectada del backend.

---

## Git y ciclo de vida
- revisar el gitdetail.md

---

## Ante la incertidumbre
  - Si hay dos formas válidas de resolver algo y no está claro cuál prefiere Nico: **preguntar antes de inferir**.
  - No asumir estructura, ubicación de archivos, ni nombres sin confirmación cuando hay ambigüedad real.
  - Cambios que afecten configuración (`angular.json`, `tsconfig`, `app.config.ts`) deben avisarse antes de ejecutarse.
