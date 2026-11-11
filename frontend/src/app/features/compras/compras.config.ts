export const COMPRAS_CONFIG = {
  eyebrow: 'ABASTECIMIENTO · REPOSICIÓN',

  titulo: 'Lista de compras',

  descripcion:
    'Revisá los repuestos sugeridos para compra según disponibilidad y umbral.',

  cargando: 'Cargando repuestos...',

  error: 'No se pudieron cargar los repuestos.',

  vacio: 'No hay repuestos para mostrar.',

  buscar: 'Buscar',

  buscarPlaceholder:
    'Buscar por nombre o código',

  generar:
    'Generar orden de compra',

  filtros: {
    sinStock: 'Sin stock',
    bajoMinimo: 'Bajo mínimo',
    normal: 'Stock normal',
  },

  columnas: {
    repuesto: 'Repuesto',
    disponible: 'Disponible',
    minimo: 'Mínimo',
    cantidad: 'Cantidad sugerida',
    urgencia: 'Urgencia',
    motivo: 'Motivo',
  },

  resumen: {
    seleccionados: 'repuestos seleccionados',
    prioridad: 'Prioridad',
  },

  urgencias: {
    urgente: 'Urgente',
    bajoMinimo: 'Bajo mínimo',
    normal: 'Normal',
  },
} as const;