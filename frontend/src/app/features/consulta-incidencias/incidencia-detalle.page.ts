import { Component, DestroyRef, computed, inject, signal } from '@angular/core';

import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';

import {
  ROLES_CONSULTA_REPARACION,
  ROLES_REPARACION,
  tieneAlgunRol,
} from '../../core/auth/roles.guard';
import { SessionService } from '../../core/auth/session.service';
import { ToastService } from '../../core/services/toast.service';

import {
  CONSULTA_INCIDENCIAS_CONFIG,
  ESTADOS_INCIDENCIA,
  ESTADOS_REPARACION,
} from './consulta-incidencias.config';

import { IncidenciaDto, ReparacionDto } from './consulta-incidencias.models';

import { ConsultaIncidenciasService } from './consulta-incidencias.service';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
  selector: 'app-incidencia-detalle-page',
  standalone: true,
  imports: [RouterLink, HlmBadgeImports, HlmButtonImports, HlmCardImports],
  templateUrl: './incidencia-detalle.page.html',
})
export class IncidenciaDetallePage {
  private readonly servicio = inject(ConsultaIncidenciasService);

  private readonly destroyRef = inject(DestroyRef);

  private readonly ruta = inject(ActivatedRoute);

  protected readonly config = CONSULTA_INCIDENCIAS_CONFIG;

  protected readonly incidencia = signal<IncidenciaDto | null>(null);

  protected readonly carga = signal<Carga>('cargando');

  private readonly router = inject(Router);

  private readonly sesion = inject(SessionService);

  private readonly toast = inject(ToastService);

  protected readonly reparacion = signal<ReparacionDto | null>(null);

  protected readonly resumen = signal('');

  protected readonly procesando = signal(false);

  /** CUN-01: solo el empleado de mantenimiento toma, registra usos y finaliza. */
  protected readonly repara = computed(() => tieneAlgunRol(this.sesion.roles(), ROLES_REPARACION));

  /** El operario no consulta reparaciones: solo sigue el estado de la incidencia. */
  private readonly veReparacion = computed(() =>
    tieneAlgunRol(this.sesion.roles(), ROLES_CONSULTA_REPARACION),
  );

  /** Se puede tomar una incidencia reportada o en triage que todavía no tiene reparación. */
  protected readonly puedeTomar = computed(() => {
    const inc = this.incidencia();
    return (
      this.repara() &&
      inc !== null &&
      inc.reparacion_id === null &&
      ['reportada', 'en_triage'].includes(inc.estado)
    );
  });

  protected readonly reparacionEnCurso = computed(() => this.reparacion()?.estado === 'en_curso');

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    const id = Number(this.ruta.snapshot.paramMap.get('id'));

    this.carga.set('cargando');

    this.servicio
      .obtenerPorId(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (incidencia: IncidenciaDto) => {
          this.incidencia.set(incidencia);
          this.carga.set('listo');
          this.cargarReparacion(incidencia);
        },

        error: () => {
          this.carga.set('error');
        },
      });
  }

  private cargarReparacion(incidencia: IncidenciaDto): void {
    this.reparacion.set(null);
    if (incidencia.reparacion_id === null || !this.veReparacion()) {
      return;
    }
    this.servicio
      .obtenerReparacion(incidencia.reparacion_id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (reparacion) => this.reparacion.set(reparacion),
        error: () => this.reparacion.set(null),
      });
  }

  /** Toma la incidencia y lleva a registrar los repuestos usados. */
  protected tomar(inc: IncidenciaDto): void {
    this.procesando.set(true);
    this.servicio
      .tomar(inc.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (reparacion) => {
          this.procesando.set(false);
          this.toast.show({
            variant: 'success',
            title: this.config.reparacion.tomada,
            message: this.config.reparacion.tomadaMensaje,
          });
          this.router.navigate(['/usos/nuevo'], {
            queryParams: { reparacion: reparacion.id, incidencia: inc.id },
          });
        },
        error: (error) => this.fallo(error),
      });
  }

  protected finalizar(reparacion: ReparacionDto): void {
    const resumen = this.resumen().trim();
    if (!resumen) {
      this.toast.show({
        variant: 'error',
        title: this.config.reparacion.error,
        message: this.config.reparacion.resumenRequerido,
      });
      return;
    }
    this.procesando.set(true);
    this.servicio
      .finalizar(reparacion.id, resumen)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.procesando.set(false);
          this.resumen.set('');
          this.toast.show({
            variant: 'success',
            title: this.config.reparacion.resuelta,
            message: this.config.reparacion.resueltaMensaje,
          });
          this.cargar();
        },
        error: (error) => this.fallo(error),
      });
  }

  private fallo(error: { error?: { mensaje?: string }; message?: string }): void {
    this.procesando.set(false);
    this.toast.show({
      variant: 'error',
      title: this.config.reparacion.error,
      message: error.error?.mensaje ?? error.message ?? '',
    });
  }

  protected estadoReparacion(valor: string): string {
    return ESTADOS_REPARACION[valor] ?? valor;
  }

  protected estado(valor: string) {
    return (
      ESTADOS_INCIDENCIA[valor] ?? {
        etiqueta: valor,
        variante: 'outline',
      }
    );
  }

  protected fecha(valor: string): string {
    return new Date(valor).toLocaleDateString('es-AR');
  }

  protected turno(valor: string): string {
    switch (valor) {
      case 'manana':
        return 'Mañana';

      case 'tarde':
        return 'Tarde';

      case 'noche':
        return 'Noche';

      default:
        return valor;
    }
  }

  protected nombreMaquina(incidencia: IncidenciaDto): string {
    return incidencia.maquina?.codigo ?? `Máquina ${incidencia.maquina_id}`;
  }
}
