import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { DataTableComponent } from '@shared/ui/table';
import { environment } from '../../../environments/environment';
import { ESTADOS_MAQUINA, MAQUINAS_CONFIG } from './maquinas.config';
import { MaquinaDto } from './maquinas.models';
import { MaquinasService } from './maquinas.service';

type Carga = 'cargando' | 'listo' | 'error';

@Component({
  selector: 'app-maquinas-page',
  standalone: true,
  imports: [
    RouterLink,
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    DataTableComponent,
  ],
  templateUrl: './maquinas.page.html',
})
export class MaquinasPage {
  private readonly servicio = inject(MaquinasService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config = MAQUINAS_CONFIG;
  protected readonly esDemo = environment.useMockData;
  protected readonly maquinas = signal<MaquinaDto[]>([]);
  protected readonly carga = signal<Carga>('cargando');
  protected readonly busqueda = signal('');
  protected readonly tipoSeleccionado = signal('');
  protected readonly estadoSeleccionado = signal('');

  protected readonly tipos = computed(() => {
    const tipos = new Map<number, string>();
    for (const maquina of this.maquinas()) {
      tipos.set(maquina.tipo_maquina_id, maquina.tipo_maquina.nombre);
    }
    return Array.from(tipos, ([id, nombre]) => ({ id, nombre })).sort((a, b) =>
      a.nombre.localeCompare(b.nombre, 'es'),
    );
  });

  protected readonly estados = computed(() =>
    [...new Set(this.maquinas().map((maquina) => maquina.estado))].sort((a, b) =>
      a.localeCompare(b, 'es'),
    ),
  );

  protected readonly maquinasVisibles = computed(() => {
    const termino = this.busqueda().trim().toLocaleLowerCase('es');
    const tipo = this.tipoSeleccionado();
    const estado = this.estadoSeleccionado();

    return this.maquinas().filter((maquina) => {
      const coincideTipo = !tipo || String(maquina.tipo_maquina_id) === tipo;
      const coincideEstado = !estado || maquina.estado === estado;
      const coincideBusqueda =
        !termino ||
        [
          maquina.codigo,
          maquina.numero_serie ?? '',
          maquina.tipo_maquina.nombre,
          maquina.estado,
        ].some((valor) => valor.toLocaleLowerCase('es').includes(termino));

      return coincideTipo && coincideEstado && coincideBusqueda;
    });
  });

  constructor() {
    this.cargar();
  }

  protected cargar(): void {
    this.carga.set('cargando');
    this.servicio
      .listar()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (maquinas) => {
          this.maquinas.set(maquinas);
          this.carga.set('listo');
        },
        error: () => this.carga.set('error'),
      });
  }

  protected cambiarBusqueda(event: Event): void {
    this.busqueda.set((event.target as HTMLInputElement).value);
  }

  protected cambiarTipo(event: Event): void {
    this.tipoSeleccionado.set((event.target as HTMLSelectElement).value);
  }

  protected cambiarEstado(event: Event): void {
    this.estadoSeleccionado.set((event.target as HTMLSelectElement).value);
  }

  protected limpiarFiltros(): void {
    this.busqueda.set('');
    this.tipoSeleccionado.set('');
    this.estadoSeleccionado.set('');
  }

  protected estado(valor: string) {
    return ESTADOS_MAQUINA[valor] ?? { etiqueta: valor, variante: 'outline' as const };
  }

  protected fecha(valor: string | null | undefined): string {
    return valor ? new Date(valor).toLocaleDateString('es-AR') : this.config.detalle.noInformado;
  }
}
