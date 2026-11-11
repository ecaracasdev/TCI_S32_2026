import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { DataTableComponent } from '@shared/ui/table';

import {
  CONSULTA_INCIDENCIAS_CONFIG,
  ESTADOS_INCIDENCIA,
} from './consulta-incidencias.config';

import { ConsultaIncidenciasService } from './consulta-incidencias.service';

import {
  IncidenciaDto,
} from './consulta-incidencias.models';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
  selector: 'app-consulta-incidencias-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    DataTableComponent,
  ],
  templateUrl: './consulta-incidencias.page.html',
})
export class ConsultaIncidenciasPage {

  private readonly servicio =
    inject(ConsultaIncidenciasService);

  private readonly destroyRef =
    inject(DestroyRef);

  protected readonly config =
    CONSULTA_INCIDENCIAS_CONFIG;

  protected readonly incidencias =
    signal<IncidenciaDto[]>([]);

  protected readonly carga =
    signal<Carga>('cargando');

  constructor() {
    this.cargar();
  }

  protected cargar(): void {

    this.carga.set('cargando');

    this.servicio
      .listar()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (items) => {
          this.incidencias.set(items);
          this.carga.set('listo');
        },

        error: () => {
          this.carga.set('error');
        },
      });
  }

  protected nombreMaquina(
    incidencia: IncidenciaDto,
  ): string {

    return `${incidencia.maquina.tipo_maquina.nombre} ${incidencia.maquina.codigo}`;
  }

  protected estado(valor: string) {

    return (
      ESTADOS_INCIDENCIA[valor] ?? {
        etiqueta: valor.replaceAll('_', ' '),
        variante: 'outline',
      }
    );
  }

  protected fecha(
    valor: string,
  ): string {

    return new Date(valor).toLocaleDateString(
      'es-AR',
    );
  }

  protected turno(
    valor: string,
  ): string {

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
}