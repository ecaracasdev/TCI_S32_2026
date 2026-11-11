export const REPOSICION_REPUESTOS_CONFIG = {
  eyebrow: 'ALMACÉN · REPOSICIÓN',

  titulo: 'Repuestos para reposición',

  descripcion:
    'Consultá los repuestos que requieren reposición por encontrarse sin stock o por debajo del umbral mínimo.',

  cargando: 'Cargando repuestos...',

  error: 'No se pudieron cargar los repuestos.',

  vacio: 'No hay repuestos para reposición.',

  reintentar: 'Reintentar',

  buscar: 'Buscar repuestos',

  buscarPlaceholder:
    'Buscar por nombre o código',

  filtrar: 'Filtrar por estado',

  mostrando: 'Mostrando',

  de: 'de',

  sinDato: '—',

  filtros: {
    todos: 'Todos',
    sinStock: 'Sin stock',
    bajoMinimo: 'Bajo mínimo',
  },

  columnas: {
    repuesto: 'Repuesto',
    disponible: 'Disponible',
    minimo: 'Mínimo',
    ubicacion: 'Ubicación',
    motivo: 'Motivo',
  },
} as const;