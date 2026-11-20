import {
  ROLES_CONSULTA_INCIDENCIAS,
  ROLES_LECTURA_PLANTA,
  ROLES_REPARACION,
  ROLES_REPORTE_INCIDENCIA,
} from '../../core/auth/roles.guard';

/** Cada módulo indica qué roles lo ven; sin `roles`, lo ven todos. */
export const HEADER_CONFIG = {
  brand: {
    name: 'TCI',
    homeUrl: '/',
  },
  navigation: [
    { label: 'Inicio', href: '/inicio' },
    { label: 'Reportar incidencia', href: '/incidencias/nueva', roles: ROLES_REPORTE_INCIDENCIA },
    { label: 'Incidencias', href: '/incidencias', roles: ROLES_CONSULTA_INCIDENCIAS },
    { label: 'Registrar uso', href: '/usos/nuevo', roles: ROLES_REPARACION },
    { label: 'Máquinas', href: '/maquinas', roles: ROLES_LECTURA_PLANTA },
    { label: 'Repuestos', href: '/stock', roles: ROLES_LECTURA_PLANTA },
    { label: 'Ubicaciones', href: '/ubicaciones', roles: ROLES_LECTURA_PLANTA },
    { label: 'Reposición', href: '/reposicion', roles: ROLES_LECTURA_PLANTA },
    { label: 'Compras', href: '/compras', roles: ROLES_LECTURA_PLANTA },
  ] as { label: string; href: string; roles?: string[] }[],
};
