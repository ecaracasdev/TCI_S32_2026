export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export type EstadoPedido =
  | 'creado'
  | 'pendiente_revision'
  | 'pendiente_aprobacion'
  | 'confirmado'
  | 'cancelado'
  | 'pendiente_recepcion'
  | 'recibido';

export type UrgenciaCompra = 'normal' | 'urgente';
export type OrigenCompra = 'manual' | 'automatico';

export interface RepuestoResumenDto {
  id: number;
  codigo: string;
  nombre: string;
}

export interface ItemPedidoCompraDto {
  id: number;
  repuesto: RepuestoResumenDto;
  cantidad_solicitada: number;
}

export interface UbicacionDto {
  id: number;
  codigo: string;
  descripcion?: string | null;
}

export interface ItemRecepcionCompraDto {
  id: number;
  item_pedido_compra_id: number;
  ubicacion: UbicacionDto;
  cantidad: number;
}

export interface ItemRecepcionCompraCreateDto {
  item_pedido_compra_id: number;
  ubicacion_id: number;
  cantidad: number;
}

export interface RecepcionCompraCreateDto {
  delegada_a_usuario_id?: number | null;
  notas?: string | null;
  items: ItemRecepcionCompraCreateDto[];
}

export interface RecepcionCompraDto {
  id: number;
  pedido_compra_id: number;
  recibida_por_usuario_id: number;
  delegada_a_usuario_id?: number | null;
  recibida_en: string;
  notas?: string | null;
  items?: ItemRecepcionCompraDto[];
}

export interface PedidoCompraDto {
  id: number;
  creada_por_usuario_id: number;
  asignado_a_usuario_id?: number | null;
  revision_resuelta_por_usuario_id?: number | null;
  revision_resuelta_en?: string | null;
  urgencia: UrgenciaCompra;
  origen: OrigenCompra;
  estado: EstadoPedido;
  motivo?: string | null;
  motivo_cancelacion?: string | null;
  creado_en: string;
  items?: ItemPedidoCompraDto[];
  recepciones?: RecepcionCompraDto[];
}
