# 🤝 TEAM_CHARTER.md

> Reglas de convivencia y trabajo del equipo para el TCI · Desarrollo de Software 2026 · Comisión S32.

## Integrantes

| Legajo | Nombre y apellido | Email                       |
| ------ | ------------------ | ---------------------------- |
| 34575  | ELIAS, CARACAS      | ecaracasdev@gmail.com        |
| 32520  | Martin, Carrasco    | carrascomartin532@gmail.com  |

## Canal de comunicación y frecuencia mínima de encuentro

- **Canal oficial:** grupo de WhatsApp del equipo.
- **Frecuencia mínima:** una reunión semanal (virtual o presencial) para revisar avances y bloqueos.
- **Tiempo de respuesta esperado:** cada integrante responde mensajes del grupo dentro de las 24 h hábiles.
- Cualquier ausencia a una reunión debe avisarse con anticipación en el grupo.

## Convención de commits

Usamos **Conventional Commits**:

```
<tipo>: <descripción corta en minúscula, en modo imperativo>
```

Tipos permitidos:

| Tipo       | Uso                                                    |
| ---------- | ------------------------------------------------------- |
| `feat`     | Nueva funcionalidad                                     |
| `fix`      | Corrección de un bug                                    |
| `docs`     | Cambios de documentación (README, charter, etc.)        |
| `chore`    | Tareas de mantenimiento (deps, configuración, etc.)      |
| `refactor` | Cambio de código que no agrega funcionalidad ni corrige bugs |
| `test`     | Agregar o corregir tests                                 |

Ejemplo: `feat: agregar endpoint de login`

## Reglas de pull requests

- **Quién aprueba:** todo PR necesita **al menos 1 aprobación** de un compañero que no sea el autor. El autor **no se mergea su propio PR**.
- **Título del PR:** debe seguir la misma convención que los commits (`tipo: descripción corta`), reflejando el cambio principal.
- **Protección de `main`:** la rama `main` está protegida vía *ruleset* de GitHub — no se permite push directo, solo merge de PRs con al menos 1 review aprobado.
- Todo PR debe describir brevemente **qué** cambia y **por qué**.

## Definición de "terminado" (Definition of Done)

Un cambio se considera terminado cuando:

1. El código/documentación cumple lo pedido en la consigna.
2. Pasó por PR y tiene al menos 1 aprobación.
3. No rompe nada existente (se probó localmente lo que aplica).
4. Está mergeado a `main` del fork del equipo.

## Qué pasa si alguien no aporta

- Si un integrante no responde ni aporta durante **más de una semana** sin aviso, se lo consulta directamente en el grupo.
- Si la situación persiste, se informa a la cátedra según el mecanismo que indique la consigna del TCI, dejando registro de los intentos de contacto.
- El objetivo es siempre resolver internamente primero, con comunicación clara y a tiempo.
