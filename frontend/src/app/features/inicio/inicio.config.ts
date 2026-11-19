/** Textos de la vista de inicio*/
export const INICIO_CONFIG = {
  eyebrow: 'OPERACIÓN DE PLANTA',
  titulo: 'Inicio del sistema',
  descripcion: 'Accedé rápidamente a las tareas de mantenimiento de la planta.',
  reportar: 'Reportar incidencia',
  verMaquinas: 'Consultar máquinas',
  reintentar: 'Reintentar',
  demo: 'Datos de demostración: no se guardan en el backend ni se envían notificaciones.',
  incidencias: {
    titulo: 'Incidencias recientes',
    descripcion: 'Reportes que necesitan seguimiento',
    verTodas: 'Ver todas',
    cargando: 'Cargando incidencias…',
    error: 'No se pudieron cargar las incidencias.',
    vacio: 'No hay incidencias recientes.',
    columnas: {
      maquina: 'Máquina',
      incidencia: 'Incidencia',
      reportada: 'Reportada',
      estado: 'Estado',
    },
  },
  repuestos: {
    titulo: 'Repuestos por reponer',
    descripcion: 'Disponibilidad igual o menor al mínimo',
    inventario: 'Inventario',
    revisarCompras: 'Revisar lista de compras',
    verPedidos: 'Consultar pedidos de compra',
    minimo: 'Mín.',
    cargando: 'Cargando repuestos…',
    error: 'No se pudieron cargar los repuestos.',
    vacio: 'No hay repuestos bajo el mínimo.',
    columnas: { repuesto: 'Repuesto', disponible: 'Disponible', minimo: 'Mínimo' },
  },
  turnos: {
    titulo: 'Operación continua, tres turnos',
    texto:
      'El próximo cambio de turno está previsto para las 14:00. Los reportes mantienen su trazabilidad.',
  },
} as const;

