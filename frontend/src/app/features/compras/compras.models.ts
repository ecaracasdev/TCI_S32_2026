import { RepuestoDto } from '../repuestos/repuestos.models';

export type UrgenciaCompra =
  | 'normal'
  | 'urgente';

export interface LineaCompra {
  repuesto: RepuestoDto;

  cantidad: number;

  urgencia: UrgenciaCompra;

  seleccionado: boolean;
}

export interface ResumenCompra {
  cantidadLineas: number;

  prioridad: UrgenciaCompra;
}