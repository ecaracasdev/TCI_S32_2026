export interface Pagina<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface FotoDto {
  nombre_archivo: string;
  tipo_mime: string;
  contenido_base64: string;
}

export interface IncidenciaDto {
  id: number;

  descripcion: string;

  estado: string;

  turno: string;

  reportada_en: string;

  resuelta_en: string | null;

  reportada_por_usuario_id?: number;

  fotos: FotoDto[];

  maquina: {
    codigo: string;

    tipo_maquina: {
      nombre: string;
    };
  };
}