import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { SessionService } from './session.service';

/** Roles que consultan máquinas y el almacén (docs/actores.md). El operario no accede. */
export const ROLES_LECTURA_PLANTA = [
  'empleado_mantenimiento',
  'encargado_mantenimiento',
  'gerencia_administracion',
];

/** Acordado con el equipo: solo el operario reporta incidencias; todos los roles las consultan. */
export const ROLES_REPORTE_INCIDENCIA = ['operario_maquina'];
export const ROLES_CONSULTA_INCIDENCIAS = ['operario_maquina', ...ROLES_LECTURA_PLANTA];

/** CUN-01: el empleado toma la incidencia, registra los repuestos usados y la resuelve. */
export const ROLES_REPARACION = ['empleado_mantenimiento'];
export const ROLES_CONSULTA_REPARACION = ROLES_LECTURA_PLANTA;

/** CUN-03: el encargado gestiona los pedidos de compra; gerencia solo los consulta. */
export const ROLES_CONSULTA_PEDIDOS = ['encargado_mantenimiento', 'gerencia_administracion'];
export const ROLES_GESTION_PEDIDOS = ['encargado_mantenimiento'];

export function tieneAlgunRol(roles: string[], permitidos: string[]): boolean {
  return roles.some((rol) => permitidos.includes(rol.toLowerCase()));
}

/**
 * Deja entrar solo a los roles indicados; el resto vuelve a inicio.
 * Si el perfil todavía no se cargó (por ejemplo, al recargar la página), lo pide antes de decidir.
 */
export function rolGuard(permitidos: string[]): CanActivateFn {
  return () => {
    const sesion = inject(SessionService);
    const router = inject(Router);
    const decidir = (roles: string[]) =>
      tieneAlgunRol(roles, permitidos) || router.createUrlTree(['/inicio']);

    const usuario = sesion.usuario();
    if (usuario) {
      return decidir(usuario.roles);
    }
    return sesion.cargarPerfil().pipe(
      map((perfil) => decidir(perfil.roles)),
      catchError(() => of(router.createUrlTree(['/login']))),
    );
  };
}
