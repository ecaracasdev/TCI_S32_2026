
export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface FotoDto {
  id: number;
  nombre_archivo: string | null;
  tipo_mime: string;
  capturada_en: string | null;
  contenido_base64: string;
}

export interface IncidenciaDto {
  id: number;
  maquina_id: number;

  descripcion: string;
  estado: string;
  turno: string;
  reportada_en: string;
  resuelta_en: string | null;
  reportada_por_usuario_id: number;
  /** Reparación de la incidencia, si un empleado ya la tomó. */
  reparacion_id: number | null;

  fotos: FotoDto[];

  maquina: {
    id: number;
    codigo: string;
  } | null;
}

export interface UsoRepuestoDto {
  id: number;
  cantidad: number;
  usada_en: string;
  repuesto: { id: number; codigo: string; nombre: string };
}

export interface ReparacionDto {
  id: number;
  incidencia_id: number;
  empleado_id: number | null;
  /** en_curso, pendiente_repuesto o completada. */
  estado: string;
  iniciada_en: string | null;
  completada_en: string | null;
  usos: UsoRepuestoDto[];
  informe_resolucion: { resumen: string; creada_en: string } | null;
}
