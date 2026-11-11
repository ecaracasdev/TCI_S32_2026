import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { SearchComponent, type SearchFunction } from '@shared/ui/search';
import { DataTableComponent } from '@shared/ui/table';
import { RepuestoDto, estadoDe } from '../repuestos/repuestos.models';
import { RepuestosService } from '../repuestos/repuestos.service';
import { COMPRAS_CONFIG } from './compras.config';

type Carga = 'cargando' | 'listo' | 'error';
type Vista = 'sin_stock' | 'bajo_minimo' | 'normal';
type Urgencia = 'normal' | 'urgente';

const CANTIDAD_MAXIMA = 9999;

/** Minúsculas y sin tildes, para que "valvula" encuentre "Válvula". */
const normalizar = (texto: string): string =>
  texto.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');

@Component({
  selector: 'app-compras-page',
  standalone: true,
  imports: [HlmBadgeImports, HlmButtonImports, HlmCardImports, SearchComponent, DataTableComponent],
  templateUrl: './compras.page.html',
})
export class ComprasPage {
  private readonly servicio = inject(RepuestosService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly config = COMPRAS_CONFIG;

  protected readonly carga = signal<Carga>('cargando');
  protected readonly termino = signal('');
  protected readonly vista = signal<Vista>('sin_stock');
  protected readonly mostrarResumen = signal(false);
  protected readonly repuestos = signal<RepuestoDto[]>([]);

  /** Cantidad a pedir por repuesto (id -> cantidad). 0 marca un valor inválido escrito a mano. */
  protected readonly cantidades = signal<Record<number, number>>({});

  /**
   * Ids de los repuestos tildados. Es independiente de la pestaña, la búsqueda y la página:
   * cambiar de pestaña no deselecciona nada.
   */
  protected readonly seleccion = signal<ReadonlySet<number>>(new Set<number>());

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
          const activos = items.filter((item) => item.activo);
          const cantidades: Record<number, number> = {};
          for (const item of activos) {
            cantidades[item.id] = this.cantidadSugerida(item);
          }

          this.cantidades.set(cantidades);
          // Como en el mockup, arrancan tildados los que ya llegaron al umbral. El usuario puede
          // destildarlos y no se crea nada hasta que confirme.
          this.seleccion.set(new Set(activos.filter((item) => estadoDe(item) !== 'normal').map((item) => item.id)));
          this.repuestos.set(activos);
          this.carga.set('listo');
        },
        error: () => {
          this.carga.set('error');
        },
      });
  }

  // ---------- Búsqueda y pestañas ----------

  protected readonly buscar: SearchFunction<RepuestoDto> = (_items, termino) => {
    this.termino.set(termino);
  };

  protected elegirVista(vista: Vista): void {
    this.vista.set(vista);
  }

  /** Repuestos que coinciden con la búsqueda (los contadores de las pestañas parten de acá). */
  private readonly buscados = computed(() => {
    const texto = normalizar(this.termino().trim());
    if (!texto) return this.repuestos();
    return this.repuestos().filter((r) => normalizar(`${r.nombre} ${r.codigo}`).includes(texto));
  });

  protected contar(vista: Vista): number {
    return this.buscados().filter((r) => estadoDe(r) === vista).length;
  }

  /** Lo que se muestra en pantalla: pestaña actual + búsqueda. */
  protected readonly visibles = computed(() => this.buscados().filter((r) => estadoDe(r) === this.vista()));

  // ---------- Selección ----------

  protected seleccionado(id: number): boolean {
    return this.seleccion().has(id);
  }

  protected alternar(id: number, marcado: boolean): void {
    this.seleccion.update((actual) => {
      const copia = new Set(actual);
      if (marcado) copia.add(id);
      else copia.delete(id);
      return copia;
    });
  }

  /** Casilla de la cabecera: marca o desmarca todo lo que se ve (pestaña actual + búsqueda). */
  protected readonly todosMarcados = computed(
    () => this.visibles().length > 0 && this.visibles().every((r) => this.seleccion().has(r.id)),
  );

  protected alternarTodos(marcado: boolean): void {
    this.seleccion.update((actual) => {
      const copia = new Set(actual);
      for (const r of this.visibles()) {
        if (marcado) copia.add(r.id);
        else copia.delete(r.id);
      }
      return copia;
    });
  }

  // ---------- Cantidades ----------

  /** Sugerencia provisoria: lo que falta para llegar al mínimo. TODO: confirmar con el equipo. */
  protected cantidadSugerida(r: RepuestoDto): number {
    return Math.max(1, r.stock_minimo - r.stock_disponible_total);
  }

  protected cantidad(id: number): number {
    return this.cantidades()[id] ?? 1;
  }

  protected cantidadValida(id: number): boolean {
    const cantidad = this.cantidad(id);
    return Number.isInteger(cantidad) && cantidad >= 1;
  }

  protected aumentar(id: number): void {
    this.ajustar(id, 1);
  }

  protected disminuir(id: number): void {
    this.ajustar(id, -1);
  }

  /** Para cuando la cantidad se escribe a mano en el campo. */
  protected cambiarCantidad(id: number, valor: string): void {
    const numero = Number(valor);
    const valida = valor.trim() !== '' && Number.isInteger(numero) && numero >= 1 && numero <= CANTIDAD_MAXIMA;
    this.cantidades.update((actual) => ({ ...actual, [id]: valida ? numero : 0 }));
  }

  private ajustar(id: number, delta: number): void {
    this.cantidades.update((actual) => ({
      ...actual,
      [id]: Math.min(CANTIDAD_MAXIMA, Math.max(1, (actual[id] || 1) + delta)),
    }));
  }

  // ---------- Etiquetas ----------

  protected motivo(r: RepuestoDto): string {
    const estado = estadoDe(r);
    if (estado === 'sin_stock') return 'Sin stock';
    if (estado === 'bajo_minimo') return 'Bajo mínimo';
    return 'Stock normal';
  }

  /** Columna "Motivo": por qué el repuesto está en la lista. */
  protected badgeMotivo(r: RepuestoDto) {
    const estado = estadoDe(r);
    if (estado === 'sin_stock') return { etiqueta: this.motivo(r), variante: 'destructive' as const };
    if (estado === 'bajo_minimo') return { etiqueta: this.motivo(r), variante: 'outline' as const };
    return { etiqueta: this.motivo(r), variante: 'secondary' as const };
  }

  /** Columna "Urgencia": solo existen normal y urgente (urgente cuando no hay stock). */
  protected badge(r: RepuestoDto) {
    return estadoDe(r) === 'sin_stock'
      ? { etiqueta: 'Urgente', variante: 'destructive' as const }
      : { etiqueta: 'Normal', variante: 'secondary' as const };
  }

  // ---------- Resumen del pedido ----------

  /** Los repuestos tildados, de todas las pestañas y páginas. */
  protected readonly seleccionados = computed(() => this.repuestos().filter((r) => this.seleccion().has(r.id)));

  protected readonly totalSeleccionados = computed(() => this.seleccionados().length);

  /** Líneas del pedido: lo que se muestra en la revisión y lo que se enviaría al backend. */
  protected readonly lineas = computed(() =>
    this.seleccionados().map((repuesto) => ({ repuesto, cantidad: this.cantidad(repuesto.id) })),
  );

  /** Valor para el contrato: PedidoCompraCreateDto.urgencia es 'normal' o 'urgente' (minúscula). */
  protected readonly urgencia = computed<Urgencia>(() =>
    this.seleccionados().some((r) => estadoDe(r) === 'sin_stock') ? 'urgente' : 'normal',
  );

  /** Texto para mostrar en pantalla. */
  protected readonly prioridadGeneral = computed(() => (this.urgencia() === 'urgente' ? 'Urgente' : 'Normal'));

  protected readonly hayCantidadInvalida = computed(() => this.seleccionados().some((r) => !this.cantidadValida(r.id)));

  protected readonly puedeRevisar = computed(() => this.totalSeleccionados() > 0 && !this.hayCantidadInvalida());

  protected abrirResumen(): void {
    if (this.puedeRevisar()) {
      this.mostrarResumen.set(true);
    }
  }

  protected cerrarResumen(): void {
    this.mostrarResumen.set(false);
  }
}