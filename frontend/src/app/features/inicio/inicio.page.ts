import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { type BadgeVariants, HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { IconComponent } from '@shared/ui/icon';
import { DataTableComponent } from '@shared/ui/table';
import { environment } from '../../../environments/environment';
import { ESTADOS_INCIDENCIA, INICIO_CONFIG } from './inicio.config';
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

  /**
   * Gerencia/Administración es solo lectura: no ve acciones.
   * TODO: derivarlo de los roles de GET /api/v0/auth/me ('gerencia_administracion')
   * cuando exista autenticación.
   */
  protected readonly soloLectura = false;

  constructor() {
    this.cargarIncidencias();
    this.cargarAlertas();
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
    return `${incidencia.maquina.tipo_maquina.nombre} ${incidencia.maquina.codigo}`;
  }

  /** La API devuelve un id numérico; se muestra como INC-0248. */
  protected codigoIncidencia(id: number): string {
    return `INC-${String(id).padStart(4, '0')}`;
  }

  protected estado(valor: string): { etiqueta: string; variante: BadgeVariants['variant'] } {
    return ESTADOS_INCIDENCIA[valor] ?? { etiqueta: valor.replaceAll('_', ' '), variante: 'outline' };
  }

  /** "Hace 12 min", "Hace 2 h", "Hace 1 d". */
  protected hace(fecha: string): string {
    const min = Math.max(0, Math.round((Date.now() - new Date(fecha).getTime()) / 60_000));
    if (min < 60) return `Hace ${min} min`;
    const horas = Math.floor(min / 60);
    return horas < 24 ? `Hace ${horas} h` : `Hace ${Math.floor(horas / 24)} d`;
  }
}