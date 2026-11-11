import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { SearchComponent, type SearchFunction } from '@shared/ui/search';
import { DataTableComponent } from '@shared/ui/table';

import {
  RepuestoDto,
  estadoDe,
  codigosUbicacion,
} from '../repuestos/repuestos.models';

import { RepuestosService } from '../repuestos/repuestos.service';

import { REPOSICION_REPUESTOS_CONFIG } from './reposicion-repuestos.config';

type Carga = 'cargando' | 'listo' | 'error';

const normalizar = (texto: string): string =>
  texto
    .toLocaleLowerCase('es')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

@Component({
  selector: 'app-reposicion-repuestos-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    SearchComponent,
    DataTableComponent,
  ],
  templateUrl: './reposicion-repuestos.page.html',
})
export class ReposicionRepuestosPage {
  private readonly servicio = inject(RepuestosService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config =
    REPOSICION_REPUESTOS_CONFIG;

  protected readonly carga =
    signal<Carga>('cargando');

  protected readonly repuestos =
    signal<RepuestoDto[]>([]);

  protected readonly termino =
    signal('');

  protected readonly filtro =
    signal<'todos' | 'sin_stock' | 'bajo_minimo'>(
      'todos',
    );

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
          this.repuestos.set(items);
          this.carga.set('listo');
        },

        error: () =>
          this.carga.set('error'),
      });
  }

  protected readonly buscar: SearchFunction<RepuestoDto> =
    (_coleccion, termino) => {
      this.termino.set(termino);
    };

  private readonly buscados =
    computed(() => {
      const termino =
        normalizar(this.termino().trim());

      const candidatos =
        this.repuestos().filter((r) => {
          const estado = estadoDe(r);

          return (
            estado === 'sin_stock' ||
            estado === 'bajo_minimo'
          );
        });

      if (!termino) {
        return candidatos;
      }

      return candidatos.filter((r) =>
        normalizar(
          `${r.nombre} ${r.codigo}`,
        ).includes(termino),
      );
    });

  protected readonly visibles =
    computed(() => {
      const filtro =
        this.filtro();

      if (filtro === 'todos') {
        return this.buscados();
      }

      return this.buscados().filter(
        (r) =>
          estadoDe(r) === filtro,
      );
    });

  protected elegirFiltro(
    filtro:
      | 'todos'
      | 'sin_stock'
      | 'bajo_minimo',
  ): void {
    this.filtro.set(filtro);
  }

  protected motivo(
    repuesto: RepuestoDto,
  ): string {
    const estado =
      estadoDe(repuesto);

    return estado === 'sin_stock'
      ? 'Sin stock'
      : 'Bajo mínimo';
  }

  protected ubicaciones(
    repuesto: RepuestoDto,
  ): string {
    return codigosUbicacion(
      repuesto,
    ).join(', ');
  }
}