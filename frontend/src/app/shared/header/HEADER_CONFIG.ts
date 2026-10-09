export const HEADER_CONFIG = {
    leftNavigation: [
        { label: 'Resumen', href: '/', icon: 'activity' },
        { label: 'Repuestos', href: '/stock', icon: 'boxes' },
    ],
    rightNavigation: [
        { label: 'Incidencias', href: '/incidencias', icon: 'alert' },
    ],
    overflowNavigation: [
        { label: 'Vista general', href: '/ui-preview', icon: 'activity' },
        { label: 'Compras', href: '/compras', icon: 'shoppingCart' },
        { label: 'Máquinas', href: '/maquinas', icon: 'factory' },
    ],
    roles: [
        { id: 'operator', label: 'Operario de máquina', shortLabel: 'Operario' },
        { id: 'maintenance', label: 'Empleado de mantenimiento', shortLabel: 'Mantenimiento' },
        { id: 'manager', label: 'Encargado de mantenimiento', shortLabel: 'Encargado' },
        { id: 'management', label: 'Gerencia / Administración', shortLabel: 'Gerencia' },
    ],
} as const;
