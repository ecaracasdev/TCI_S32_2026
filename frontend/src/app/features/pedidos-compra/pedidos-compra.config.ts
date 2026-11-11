import { type BadgeVariants } from '@shared/ui/badge';
import { EstadoPedido, UrgenciaCompra } from './pedidos-compra.models';

export const PEDIDOS_COMPRA_CONFIG = {
  titulo: 'Pedidos de compra',
  descripcion: 'Consultá el estado, la urgencia y la recepción de cada pedido.',
  cargando: 'Cargando pedidos de compra...',
  error: 'No se pudieron cargar los pedidos de compra.',
  vacio: 'No hay pedidos de compra para mostrar.',
  reintentar: 'Reintentar',
  volver: 'Volver a pedidos',
  columnas: {
    pedido: 'Pedido',
    creado: 'Creado',
    origen: 'Origen',
    items: 'Líneas',
    urgencia: 'Urgencia',
    estado: 'Estado',
    accion: 'Acción',
  },
  detalle: {
    cargando: 'Cargando pedido...',
    error: 'No se pudo cargar el pedido de compra.',
    creado: 'Creado',
    origen: 'Origen',
    urgencia: 'Urgencia',
    estado: 'Estado',
    motivo: 'Motivo',
    motivoCancelacion: 'Motivo de cancelación',
    lineas: 'Repuestos solicitados',
    sinLineas: 'Este pedido no tiene líneas para mostrar.',
    recepciones: 'Recepciones',
    sinRecepciones: 'Todavía no se registraron recepciones.',
    cantidad: 'Cantidad solicitada',
    ubicacion: 'Ubicación',
    recibida: 'Recibida',
    registrarRecepcion: 'Registrar recepción',
  },
  recepcion: {
    titulo: 'Registrar recepción',
    descripcion:
      'Cargá el stock físico recibido y la ubicación de cada línea. Podés registrar una recepción parcial si todavía no llegó todo el pedido.',
    demo: 'Datos de demostración: la recepción no se guarda en el backend ni actualiza el pedido real.',
    cargando: 'Cargando pedido...',
    error: 'No se pudo cargar el pedido de compra.',
    errorEnviar: 'No se pudo registrar la recepción.',
    sinPendientes: 'Este pedido no tiene líneas pendientes de recibir.',
    noDisponible:
      'Solo se puede registrar una recepción sobre un pedido confirmado o pendiente de recepción.',
    columnas: {
      repuesto: 'Repuesto',
      solicitado: 'Solicitado',
      recibidoPrevio: 'Recibido previamente',
      pendiente: 'Pendiente',
      cantidadRecibida: 'Cantidad a recibir',
      ubicacion: 'Ubicación',
    },
    elegirUbicacion: 'Elegí una ubicación',
    delegarA: 'Delegar a (ID de usuario, opcional)',
    notas: 'Notas (opcional)',
    enviar: 'Registrar recepción',
    enviando: 'Registrando...',
    cantidadInvalida: 'La cantidad no puede superar lo pendiente de recibir.',
    faltaUbicacion: 'Elegí una ubicación para cada cantidad cargada.',
    volver: 'Volver al pedido',
  },
} as const;

export const ESTADOS_PEDIDO: Record<
  EstadoPedido,
  { etiqueta: string; variante: BadgeVariants['variant'] }
> = {
  creado: { etiqueta: 'Creado', variante: 'outline' },
  pendiente_revision: { etiqueta: 'Pendiente de revisión', variante: 'secondary' },
  pendiente_aprobacion: { etiqueta: 'Pendiente de aprobación', variante: 'default' },
  confirmado: { etiqueta: 'Confirmado', variante: 'default' },
  cancelado: { etiqueta: 'Cancelado', variante: 'destructive' },
  pendiente_recepcion: { etiqueta: 'Pendiente de recepción', variante: 'secondary' },
  recibido: { etiqueta: 'Recibido', variante: 'outline' },
};

export const URGENCIAS_COMPRA: Record<
  UrgenciaCompra,
  { etiqueta: string; variante: BadgeVariants['variant'] }
> = {
  normal: { etiqueta: 'Normal', variante: 'outline' },
  urgente: { etiqueta: 'Urgente', variante: 'destructive' },
};

export const ORIGENES_COMPRA = {
  manual: 'Manual',
  automatico: 'Automático',
} as const;
