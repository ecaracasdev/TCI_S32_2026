import { Component, DestroyRef, computed, effect, inject, signal, untracked } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { type BadgeVariants, HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { IconComponent } from '@shared/ui/icon';
import { DataTableComponent } from '@shared/ui/table';
import { environment } from '../../../environments/environment';
import {
  ROLES_LECTURA_PLANTA,
  ROLES_REPORTE_INCIDENCIA,
  tieneAlgunRol,
} from '../../core/auth/roles.guard';
import { SessionService } from '../../core/auth/session.service';
import { ESTADOS_INCIDENCIA } from '../consulta-incidencias/consulta-incidencias.config';
import { INICIO_CONFIG } from './inicio.config';
import { AlertaStockDto, IncidenciaDto } from './inicio.models';
import { InicioService } from './inicio.service';

type Carga = 'cargando' | 'listo' | 'error';

/** Vista de inicio y resumen operativo: incidencias recientes y repuestos bajo el mínimo. */
@Component({
  selector: 'app-inicio-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    IconComponent,
    DataTableComponent,
  ],
  templateUrl: './inicio.page.html',
  styleUrl: './inicio.page.css',
})
export class InicioPage {
  private readonly servicio = inject(InicioService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config = INICIO_CONFIG;
  protected readonly esDemo = environment.useMockData;

  protected readonly incidencias = signal<IncidenciaDto[]>([]);
  protected readonly cargaIncidencias = signal<Carga>('cargando');
  protected readonly alertas = signal<AlertaStockDto[]>([]);
  protected readonly cargaAlertas = signal<Carga>('cargando');

  private readonly sesion = inject(SessionService);

  /** El operario no accede al almacén ni a máquinas: no ve esos accesos ni el resumen de stock. */
  protected readonly veAlmacen = computed(() =>
    tieneAlgunRol(this.sesion.roles(), ROLES_LECTURA_PLANTA),
  );

  /** Solo el operario reporta incidencias (acordado con el equipo). */
  protected readonly reportaIncidencias = computed(() =>
    tieneAlgunRol(this.sesion.roles(), ROLES_REPORTE_INCIDENCIA),
  );

  constructor() {
    // Todos los roles consultan incidencias.
    this.cargarIncidencias();
    // Los roles pueden llegar después de crear la página (al recargar): se carga una sola vez.
    let cargado = false;
    effect(() => {
      if (this.veAlmacen() && !cargado) {
        cargado = true;
        untracked(() => this.cargarAlertas());
      }
    });
  }

  protected cargarIncidencias(): void {
    this.cargaIncidencias.set('cargando');
    this.servicio
      .incidenciasRecientes()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (items) => {
          this.incidencias.set(items);
          this.cargaIncidencias.set('listo');
        },
        error: () => this.cargaIncidencias.set('error'),
      });
  }

  protected cargarAlertas(): void {
    this.cargaAlertas.set('cargando');
    this.servicio
      .alertasStock()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (items) => {
          this.alertas.set(items);
          this.cargaAlertas.set('listo');
        },
        error: () => this.cargaAlertas.set('error'),
      });
  }

  protected nombreMaquina(incidencia: IncidenciaDto): string {
    return incidencia.maquina?.codigo ?? `Máquina ${incidencia.maquina_id}`;
  }

  /** La API devuelve un id numérico; se muestra como INC-0248. */
  protected codigoIncidencia(id: number): string {
    return `INC-${String(id).padStart(4, '0')}`;
  }

  protected estado(valor: string): { etiqueta: string; variante: BadgeVariants['variant'] } {
    return (
      ESTADOS_INCIDENCIA[valor] ?? { etiqueta: valor.replaceAll('_', ' '), variante: 'outline' }
    );
  }

  /** "Hace 12 min", "Hace 2 h", "Hace 1 d". */
  protected hace(fecha: string): string {
    const min = Math.max(0, Math.round((Date.now() - new Date(fecha).getTime()) / 60_000));
    if (min < 60) return `Hace ${min} min`;
    const horas = Math.floor(min / 60);
    return horas < 24 ? `Hace ${horas} h` : `Hace ${Math.floor(horas / 24)} d`;
  }
}
