export interface RepuestoDto {
  id: number;
  codigo: string;
  nombre: string;
  stock_minimo: number;
  stock_fisico_total: number;
  stock_reservado_total: number;
  stock_disponible_total: number;
}

export interface ReparacionDto {
  id: number;
  incidencia_id: number;
  estado: string;
}

export interface UsoRepuestoCreateDto {
  repuesto_id: number;
  cantidad: number;
}

export interface UsoRepuestoResponseDto {
  id: number;
  reparacion_id: number;
  cantidad: number;
  usada_en: string;
  repuesto: {
    id: number;
    codigo: string;
    nombre: string;
  };
}
