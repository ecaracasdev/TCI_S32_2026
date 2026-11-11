import {
  Component,
  DestroyRef,
  inject,
  signal,
} from '@angular/core';

import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import {
  ActivatedRoute,
  RouterLink,
} from '@angular/router';

import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmCardImports } from '@shared/ui/card';

import {
  CONSULTA_INCIDENCIAS_CONFIG,
  ESTADOS_INCIDENCIA,
} from './consulta-incidencias.config';

import {
  IncidenciaDto,
} from './consulta-incidencias.models';

import {
  ConsultaIncidenciasService,
} from './consulta-incidencias.service';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
  selector: 'app-incidencia-detalle-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmCardImports,
  ],
  templateUrl: './incidencia-detalle.page.html',
})
export class IncidenciaDetallePage {

  private readonly servicio =
    inject(ConsultaIncidenciasService);

  private readonly destroyRef =
    inject(DestroyRef);

  private readonly ruta =
    inject(ActivatedRoute);

  protected readonly config =
    CONSULTA_INCIDENCIAS_CONFIG;

  protected readonly incidencia =
    signal<IncidenciaDto | null>(null);

  protected readonly carga =
    signal<Carga>('cargando');

  constructor() {
    this.cargar();
  }

  protected cargar(): void {

    const id = Number(
      this.ruta.snapshot.paramMap.get('id'),
    );

    this.carga.set('cargando');

    this.servicio
      .obtenerPorId(id)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (incidencia: IncidenciaDto) => {
          this.incidencia.set(incidencia);
          this.carga.set('listo');
        },

        error: () => {
          this.carga.set('error');
        },
      });
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
    return new Date(valor)
      .toLocaleDateString('es-AR');
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

  protected nombreMaquina(
    incidencia: IncidenciaDto,
  ): string {

    return `${incidencia.maquina.tipo_maquina.nombre} ${incidencia.maquina.codigo}`;
  }
}
