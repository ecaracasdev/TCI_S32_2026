# Resumen de actores

Este documento resume los actores que participan en el sistema desde el punto de vista del negocio. Un actor representa una función o responsabilidad dentro de la planta; no representa una persona concreta, una tabla de usuarios ni una clase del sistema.

## Actores humanos

### Operador de máquina

Detecta problemas en los equipos de producción e informa incidencias al área de mantenimiento.

### Empleado de mantenimiento

Analiza y resuelve reparaciones, consulta repuestos y registra los materiales utilizados.

### Supervisor de mantenimiento

Coordina el mantenimiento, controla las necesidades de repuestos, recibe materiales y autoriza operaciones sensibles.

### Responsable de gestión y administración

Consulta la información general de la planta mediante reportes, indicadores y tableros.


## Separación general de responsabilidades

```text
Operador de máquina
    Detectar y comunicar problemas

Empleado de mantenimiento
    Analizar, reparar y registrar consumos

Supervisor de mantenimiento
    Coordinar, controlar y autorizar

Responsable de gestión y administración
    Consultar y supervisar

Servicio de notificaciones
    Comunicar eventos del sistema
```

## Decisiones pendientes
- Confirmar si el nombre oficial será “supervisor” o “encargado” de mantenimiento.
- Confirmar qué tareas de administración serán exclusivamente de consulta.
- Confirmar si una persona puede tener más de un rol (se presupone que si porque no esta detallado).