import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { IconComponent } from '@shared/ui/icon';
import { PaginationComponent } from '@shared/ui/pagination';
import { SearchComponent, type SearchFunction } from '@shared/ui/search';
import { DataTableComponent } from '@shared/ui/table';
import { environment } from '../../../environments/environment';
import { ESTADOS_STOCK, FILTROS, REPUESTOS_CONFIG } from './repuestos.config';
import {
  FiltroEstado,
  RepuestoDto,
  TAMANO_PAGINA,
  cifra,
  codigosUbicacion,
  estadoDe,
  maquinasCompatibles,
} from './repuestos.models';
import { RepuestosService } from './repuestos.service';

type Carga = 'cargando' | 'listo' | 'error';

const normalizar = (texto: string): string =>
  texto.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');

@Component({
  selector: 'app-repuestos-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    IconComponent,
    DataTableComponent,
    PaginationComponent,
    SearchComponent,
  ],
  templateUrl: './repuestos.page.html',
})
export class RepuestosPage {
  private readonly servicio = inject(RepuestosService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config = REPUESTOS_CONFIG;
  protected readonly filtros = FILTROS;
  protected readonly esDemo = environment.useMockData;
  protected readonly cifra = cifra;
  protected readonly maquinas = maquinasCompatibles;
  protected readonly ubicaciones = codigosUbicacion;

  protected readonly repuestos = signal<RepuestoDto[]>([]);
  protected readonly carga = signal<Carga>('cargando');
  protected readonly termino = signal('');
  protected readonly filtro = signal<FiltroEstado>('todos');
  protected readonly pagina = signal(1);

  /** Repuestos que coinciden con la búsqueda (los contadores se calculan sobre estos). */
  private readonly buscados = computed(() => {
    const termino = normalizar(this.termino().trim());
    if (!termino) return this.repuestos();
    return this.repuestos().filter((repuesto) =>
      normalizar(
        `${repuesto.nombre} ${repuesto.codigo} ${repuesto.descripcion ?? ''} ${maquinasCompatibles(repuesto)}`,
      ).includes(termino),
    );
  });

  protected readonly conteos = computed(() => {
    const conteos: Record<FiltroEstado, number> = { todos: 0, sin_stock: 0, bajo_minimo: 0, normal: 0 };
    for (const repuesto of this.buscados()) {
      conteos.todos++;
      conteos[estadoDe(repuesto)]++;
    }
    return conteos;
  });

  protected readonly filtrados = computed(() => {
    const filtro = this.filtro();
    return filtro === 'todos' ? this.buscados() : this.buscados().filter((repuesto) => estadoDe(repuesto) === filtro);
  });

  protected readonly totalPaginas = computed(() => Math.max(1, Math.ceil(this.filtrados().length / TAMANO_PAGINA)));
  protected readonly paginaActual = computed(() => Math.min(this.pagina(), this.totalPaginas()));
  protected readonly desde = computed(() =>
    this.filtrados().length === 0 ? 0 : (this.paginaActual() - 1) * TAMANO_PAGINA + 1,
  );
  protected readonly hasta = computed(() => Math.min(this.paginaActual() * TAMANO_PAGINA, this.filtrados().length));
  protected readonly visibles = computed(() =>
    this.filtrados().slice((this.paginaActual() - 1) * TAMANO_PAGINA, this.paginaActual() * TAMANO_PAGINA),
  );

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    this.carga.set('cargando');
    this.servicio
      .listar()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (items) => {
          this.repuestos.set(items);
          this.carga.set('listo');
        },
        error: () => this.carga.set('error'),
      });
  }

  /** Callback de app-search: se ejecuta al enviar la búsqueda. */
  protected readonly buscar: SearchFunction<RepuestoDto> = (_coleccion, termino) => {
    this.termino.set(termino);
    this.pagina.set(1);
  };

  protected elegirFiltro(filtro: FiltroEstado): void {
    this.filtro.set(filtro);
    this.pagina.set(1);
  }

  protected irAPagina(pagina: number): void {
    this.pagina.set(Math.min(Math.max(1, pagina), this.totalPaginas()));
  }

  protected info(repuesto: RepuestoDto) {
    return ESTADOS_STOCK[estadoDe(repuesto)];
  }
}