import { type BadgeVariants } from '@shared/ui/badge';
import { type EstadoStock, type FiltroEstado } from './repuestos.models';

/** Textos de las vistas de repuestos, centralizados para no repetirlos en las plantillas. */
export const REPUESTOS_CONFIG = {
  eyebrow: 'ALMACÉN · REPUESTOS',
  titulo: 'Inventario de repuestos',
  descripcion: 'Consultá existencias, disponibilidad y ubicación de cada repuesto en el almacén.',
  demo: 'Datos de demostración: no se guardan en el backend ni se envían notificaciones.',
  reintentar: 'Reintentar',
  existencias: 'Existencias',
  enEstaVista: 'repuestos en esta vista',
  buscar: 'Buscar repuestos',
  buscarPlaceholder: 'Buscar repuestos',
  filtrar: 'Filtrar por estado',
  cargando: 'Cargando repuestos…',
  error: 'No se pudieron cargar los repuestos.',
  vacio: 'No hay repuestos para mostrar con este filtro.',
  mostrando: 'Mostrando',
  de: 'de',
  minimo: 'Mín.',
  sinDato: '—',
  columnas: {
    repuesto: 'Repuesto',
    maquinas: 'Máquina compatible',
    fisico: 'Físico',
    reservado: 'Reservado',
    disponible: 'Disponible',
    ubicacion: 'Ubicación',
    estado: 'Estado',
  },
  detalle: {
    volver: 'Volver al inventario',
    existencias: 'Existencias',
    fisico: 'Físico',
    reservado: 'Reservado',
    disponible: 'Disponible',
    minimo: 'Mínimo',
    ubicaciones: 'Ubicaciones',
    sinUbicaciones: 'Sin existencias registradas en ubicaciones.',
    maquinas: 'Máquinas compatibles',
    sinMaquinas: 'Sin máquinas registradas.',
    cargando: 'Cargando repuesto…',
    error: 'No se pudo cargar el repuesto.',
  },
} as const;

export const FILTROS: { id: FiltroEstado; etiqueta: string }[] = [
  { id: 'todos', etiqueta: 'Todos' },
  { id: 'sin_stock', etiqueta: 'Sin stock' },
  { id: 'bajo_minimo', etiqueta: 'Bajo mínimo' },
  { id: 'normal', etiqueta: 'Stock normal' },
];

export const ESTADOS_STOCK: Record<EstadoStock, { etiqueta: string; variante: BadgeVariants['variant'] }> = {
  sin_stock: { etiqueta: 'Sin stock', variante: 'destructive' },
  bajo_minimo: { etiqueta: 'Bajo mínimo', variante: 'outline' },
  normal: { etiqueta: 'Disponible', variante: 'secondary' },
};