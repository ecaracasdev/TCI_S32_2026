export const REPORTAR_INCIDENCIA_CONFIG = {
  titulo: 'Reportar incidencia',
  descripcion: 'Informá un problema en una máquina de la planta.',
  enviar: 'Reportar',
  enviando: 'Enviando…',
  exito: 'Incidencia reportada',
  errorGenerico: 'No se pudo reportar la incidencia. Intentá de nuevo.',
  demo: 'Datos de demostración: la incidencia no se guarda en el backend ni se envían notificaciones.',
  maquina: {
    etiqueta: 'Código de máquina',
    placeholder: 'Ej.: F-02',
    escanear: 'Escanear QR',
    requerido: 'Ingresá o escaneá el código de la máquina.',
    noEncontrada: 'No existe una máquina con ese código.',
    // TODO: escaneo simulado para la M2. La lectura real con cámara necesita HTTPS y queda para después.
    codigosDemo: ['F-02', 'B-04', 'C-01'],
  },
  descripcionCampo: {
    etiqueta: 'Descripción',
    placeholder: 'Describí el problema que observaste…',
    requerido: 'La descripción es obligatoria.',
  },
  fotos: {
    etiqueta: 'Fotos (opcional)',
    quitar: 'Quitar',
  },
  turno: {
    etiqueta: 'Turno',
    opciones: [
      { valor: 'manana', texto: 'Mañana' },
      { valor: 'tarde', texto: 'Tarde' },
      { valor: 'noche', texto: 'Noche' },
    ],
  },
} as const;
