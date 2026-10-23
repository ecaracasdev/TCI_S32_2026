export type Turno = 'manana' | 'tarde' | 'noche';

export interface FotoIncidenciaCreateDto {
    /** minLength: 1 */
    contenido_base64: string;
    /** maxLength: 255 */
    nombre_archivo?: string | null;
    /** 1–100 caracteres */
    tipo_mime: string;
    /** ISO 8601 date-time */
    capturada_en?: string | null;
}

export interface IncidenciaCreateDto {
    /** Código QR o de barras. (1–100 caracteres) */
    maquina_codigo: string;
    /** minLength: 1 */
    descripcion: string;
    turno: Turno;
    fotos?: FotoIncidenciaCreateDto[];
}

export interface IncidenciaResponseDto {
    id: number;
    descripcion: string;
    estado: string;
    turno: Turno;
    reportada_en: string;
}
