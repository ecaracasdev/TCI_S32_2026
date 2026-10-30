export const REGISTRAR_USO_CONFIG = {
  titulo: 'Registrar uso de repuesto',
  descripcion: 'Registrá los repuestos que usaste en una reparación.',
  demo: 'Datos de demostración: el uso no se guarda en el backend y el stock vuelve a su valor al recargar la página.',
  enviar: 'Registrar uso',
  enviando: 'Registrando…',
  exito: 'Uso registrado',
  stockInsuficiente: 'No hay stock disponible suficiente.',
  alertaTitulo: 'Alerta de stock mínimo',
  alertaUmbral: 'El repuesto quedó en el mínimo o por debajo. Hay que reponerlo.',
  errorGenerico: 'No se pudo registrar el uso. Intentá de nuevo.',
  repuesto: {
    etiqueta: 'Código del repuesto',
    placeholder: 'Ej.: REP-00031',
    buscar: 'Buscar',
    buscando: 'Buscando…',
    escanear: 'Escanear',
    requerido: 'Ingresá o escaneá el código del repuesto.',
    noEncontrado: 'No existe un repuesto con ese código.',
    disponible: 'Disponible',
    minimo: 'Mínimo',
    // TODO: escaneo simulado. La lectura real con cámara necesita HTTPS.
    codigosDemo: ['REP-00031', 'REP-00106', 'REP-00203'],
  },
  // TODO: el contrato no tiene un endpoint para listar reparaciones, así que el número se escribe a mano.
  reparacion: {
    etiqueta: 'N.º de reparación',
    placeholder: 'Ej.: 101',
    requerido: 'Ingresá el número de reparación.',
    noEncontrada: 'No existe una reparación con ese número.',
  },
  cantidad: {
    etiqueta: 'Cantidad',
    invalida: 'Ingresá una cantidad entera mayor a 0.',
  },
} as const;
