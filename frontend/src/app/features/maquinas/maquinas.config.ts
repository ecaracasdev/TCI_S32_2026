import { type BadgeVariants } from '@shared/ui/badge';

export const MAQUINAS_CONFIG = {
  titulo: 'Máquinas',
  descripcion: 'Consultá las máquinas registradas y sus datos de identificación.',
  demo: 'Demostración: estos datos de ejemplo no provienen de la API.',
  cargando: 'Cargando máquinas...',
  error: 'No se pudieron cargar las máquinas.',
  vacio: 'No hay máquinas para mostrar.',
  sinCoincidencias: 'No hay máquinas que coincidan con los filtros.',
  reintentar: 'Reintentar',
  volver: 'Volver a máquinas',
  buscar: 'Buscar',
  buscarPlaceholder: 'Código, número de serie, tipo o estado',
  filtroTipo: 'Tipo de máquina',
  todosTipos: 'Todos los tipos',
  filtroEstado: 'Estado',
  todosEstados: 'Todos los estados',
  limpiarFiltros: 'Limpiar filtros',
  resultados: 'máquinas',
  columnas: {
    codigo: 'Código',
    tipo: 'Tipo',
    numeroSerie: 'Número de serie',
    estado: 'Estado',
    instalacion: 'Instalación',
    accion: 'Acción',
  },
  detalle: {
    cargando: 'Cargando máquina...',
    error: 'No se pudo cargar la máquina.',
    tipo: 'Tipo de máquina',
    numeroSerie: 'Número de serie',
    estado: 'Estado',
    instalacion: 'Fecha de instalación',
    creado: 'Registrada',
    actualizado: 'Última actualización',
    noInformado: 'No informado',
  },
} as const;

export const ESTADOS_MAQUINA: Record<
  string,
  { etiqueta: string; variante: BadgeVariants['variant'] }
> = {
  operativa: { etiqueta: 'Operativa', variante: 'default' },
  detenida: { etiqueta: 'Detenida', variante: 'destructive' },
  en_mantenimiento: { etiqueta: 'En mantenimiento', variante: 'secondary' },
};
