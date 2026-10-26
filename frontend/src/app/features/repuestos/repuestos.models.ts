/** Subconjunto de docs/spec/openapi-v0.json que usa la vista de repuestos. */

export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface UbicacionResumenDto {
  id: number;
  codigo: string;
  descripcion?: string | null;
}

export interface StockUbicacionDto {
  ubicacion_id: number;
  ubicacion: UbicacionResumenDto;
  cantidad_fisica: number;
  cantidad_reservada: number;
  cantidad_disponible: number;
}

export interface MaquinaCompatibleDto {
  id: number;
  codigo: string;
  tipo_maquina: { nombre: string };
}

export interface RepuestoDto {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string | null;
  stock_minimo: number;
  activo: boolean;
  stock?: StockUbicacionDto[];
  stock_fisico_total: number;
  stock_reservado_total: number;
  stock_disponible_total: number;
  maquinas_compatibles?: MaquinaCompatibleDto[];
}

export type EstadoStock = 'sin_stock' | 'bajo_minimo' | 'normal';
export type FiltroEstado = 'todos' | EstadoStock;

export const TAMANO_PAGINA = 5;
export const LIMITE_LISTADO = 100;

export function estadoDe(repuesto: RepuestoDto): EstadoStock {
  const disponible = repuesto.stock_disponible_total;
  if (disponible <= 0) return 'sin_stock';
  if (disponible <= repuesto.stock_minimo) return 'bajo_minimo';
  return 'normal';
}

export function maquinasCompatibles(repuesto: RepuestoDto): string {
  return (repuesto.maquinas_compatibles ?? [])
    .map((maquina) => `${maquina.tipo_maquina.nombre} ${maquina.codigo}`)
    .join(', ');
}

export function codigosUbicacion(repuesto: RepuestoDto): string[] {
  return (repuesto.stock ?? []).map((stock) => stock.ubicacion.codigo);
}

export function cifra(valor: number, digitos = 3): string {
  return String(valor).padStart(digitos, '0');
}
