import { type BadgeVariants } from '@shared/ui/badge';

export const CONSULTA_INCIDENCIAS_CONFIG = {
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
  en_triage: {
    etiqueta: 'En triage',
    variante: 'outline',
  },

  en_reparacion: {
    etiqueta: 'En reparación',
    variante: 'secondary',
  },
};