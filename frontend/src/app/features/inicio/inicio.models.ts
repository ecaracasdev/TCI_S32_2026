export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface IncidenciaDto {
  id: number;
  descripcion: string;
  estado: string; 
  reportada_en: string; 
  maquina: {
    codigo: string;
    tipo_maquina: { nombre: string };
  };
}

export interface AlertaStockDto {
  repuesto: { id: number; codigo: string; nombre: string };
  stock_disponible: number;
  stock_minimo: number;
}

export const LIMITE_RESUMEN = 5;

export function masRecientes(items: IncidenciaDto[]): IncidenciaDto[] {
  return [...items]
    .sort((a, b) => Date.parse(b.reportada_en) - Date.parse(a.reportada_en))
    .slice(0, LIMITE_RESUMEN);
}