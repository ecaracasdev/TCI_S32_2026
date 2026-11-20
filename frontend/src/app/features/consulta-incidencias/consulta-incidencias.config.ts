import { type BadgeVariants } from '@shared/ui/badge';

export const REPARACION_CONFIG = {
  titulo: 'Reparación',
  tomar: 'Tomar incidencia',
  tomarAyuda: 'Al tomarla, la incidencia pasa a "En reparación" y queda a tu nombre.',
  tomada: 'Incidencia tomada',
  tomadaMensaje: 'Quedó en reparación a tu nombre. Registrá los repuestos que uses.',
  registrarUso: 'Registrar repuesto usado',
  sinUsos: 'Todavía no se registraron repuestos.',
  finalizarTitulo: 'Finalizar reparación',
  resumen: 'Resumen de lo que se hizo',
  finalizar: 'Finalizar y resolver',
  resumenRequerido: 'Escribí un resumen de la reparación.',
  resuelta: 'Incidencia resuelta',
  resueltaMensaje: 'La reparación quedó completada con su informe.',
  informe: 'Informe de resolución',
  error: 'No se pudo completar la acción',
} as const;

export const CONSULTA_INCIDENCIAS_CONFIG = {
  reparacion: REPARACION_CONFIG,
  titulo: 'Consulta de incidencias',
  descripcion: 'Visualización de incidencias reportadas.',

  cargando: 'Cargando incidencias…',
  error: 'No se pudieron cargar las incidencias.',
  vacio: 'No hay incidencias para mostrar.',
  reintentar: 'Reintentar',

  columnas: {
    maquina: 'Máquina',
    descripcion: 'Incidencia',
    reportada: 'Fecha',
    turno: 'Turno',
    estado: 'Estado',
    evidencia: 'Evidencia',
    accion: 'Acción',
  },

  detalle: {
    volver: 'Volver a incidencias',
    tituloEvidencias: 'Evidencias',
    sinEvidencias: 'Sin evidencias adjuntas.',
    maquina: 'Máquina',
    fecha: 'Fecha',
    turno: 'Turno',
    estado: 'Estado',
    descripcion: 'Descripción',
  },
} as const;

export const ESTADOS_INCIDENCIA: Record<
  string,
  {
    etiqueta: string;
    variante: BadgeVariants['variant'];
  }
> = {
  reportada: {
    etiqueta: 'Reportada',
    variante: 'outline',
  },

  en_triage: {
    etiqueta: 'En triage',
    variante: 'outline',
  },

  en_reparacion: {
    etiqueta: 'En reparación',
    variante: 'secondary',
  },

  pendiente_repuesto: {
    etiqueta: 'Pendiente de repuesto',
    variante: 'outline',
  },

  resuelta: {
    etiqueta: 'Resuelta',
    variante: 'default',
  },
};

export const ESTADOS_REPARACION: Record<string, string> = {
  en_curso: 'En curso',
  pendiente_repuesto: 'Pendiente de repuesto',
  completada: 'Completada',
};