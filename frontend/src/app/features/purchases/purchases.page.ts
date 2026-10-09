import { Component, computed, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { IconComponent } from '@shared/ui/icon';
import { DataTableComponent } from '@shared/ui/table';
import { PaginationComponent } from '@shared/ui/pagination';
import { OrderReviewDialogComponent } from './components/order-review-dialog.component';

type StockFilter = 'out' | 'low' | 'normal';

const PURCHASES_CONFIG = {
  title: 'Lista de compras',
  description: 'Revisá los repuestos que llegaron al umbral mínimo y prepará su reposición.',
  confirmedMessage: 'Simulación finalizada. No se registró ni se envió una orden real.',
  filtersLabel: 'Filtrar repuestos por nivel de stock',
  pageSizeLabel: 'Mostrar por página',
  searchLabel: 'Buscar en esta categoría por código o nombre',
  searchPlaceholder: 'Buscar por código o nombre',
  orderHistory: [
    { code: 'PC-0084', items: 3, date: 'Hoy · 07:54', status: 'Pendiente' },
    { code: 'PC-0081', items: 5, date: 'Ayer · 16:20', status: 'En camino' },
  ],
  pageSizes: [10, 20] as const,
  filters: [
    { value: 'out', label: 'Sin stock' },
    { value: 'low', label: 'Bajo mínimo' },
    { value: 'normal', label: 'Stock normal' },
  ] as const,
  items: [
    { name: 'Rodamiento 6205-2RS', code: 'REP-00142', available: 2, minimum: 5, suggested: 8, urgency: 'Bajo mínimo', tone: 'warning', stockGroup: 'low', reason: 'Bajo mínimo', machine: 'Fraccionador F-02' },
    { name: 'Filtro de aceite FO-18', code: 'REP-00087', available: 4, minimum: 6, suggested: 6, urgency: 'Bajo mínimo', tone: 'warning', stockGroup: 'low', reason: 'Bajo mínimo', machine: 'Caldera C-01' },
    { name: 'Correa dentada HTD-8M', code: 'REP-00203', available: 0, minimum: 3, suggested: 5, urgency: 'Urgente', tone: 'danger', stockGroup: 'out', reason: 'Sin stock', machine: 'Banda B-04' },
    { name: 'Junta tórica NBR 40 mm', code: 'REP-00031', available: 14, minimum: 8, suggested: 4, urgency: 'Normal', tone: 'good', stockGroup: 'normal', reason: 'Previsión preventiva', machine: 'Fraccionador F-01' },
  ],
};

@Component({
  selector: 'app-purchases-page',
  standalone: true,
  imports: [RouterLink, DecimalPipe, HlmButtonImports, HlmCardImports, HlmBadgeImports, IconComponent, DataTableComponent, PaginationComponent, OrderReviewDialogComponent],
  templateUrl: './purchases.page.html',
  styleUrl: './purchases.page.css',
})
export class PurchasesPage {
  protected readonly config = PURCHASES_CONFIG;
  protected readonly orderReviewOpen = signal(false);
  protected readonly orderResult = signal<{ code: string; itemCount: number; priority: string } | null>(null);
  protected readonly activeFilter = signal<StockFilter>('out');
  protected readonly searches = signal<Record<StockFilter, string>>({ out: '', low: '', normal: '' });
  protected readonly pages = signal<Record<StockFilter, number>>({ out: 1, low: 1, normal: 1 });
  protected readonly pageSize = signal<(typeof PURCHASES_CONFIG.pageSizes)[number]>(10);
  protected readonly selectedCodes = signal(new Set(PURCHASES_CONFIG.items.slice(0, 3).map((item) => item.code)));
  protected readonly filteredItems = computed(() => {
    const filter = this.activeFilter();
    const term = this.searches()[filter].trim().toLocaleLowerCase('es');
    return PURCHASES_CONFIG.items.filter((item) => item.stockGroup === filter
      && (!term || `${item.code} ${item.name}`.toLocaleLowerCase('es').includes(term)));
  });
  protected readonly pageCount = computed(() => Math.max(1, Math.ceil(this.filteredItems().length / this.pageSize())));
  protected readonly visibleItems = computed(() => {
    const start = (this.pages()[this.activeFilter()] - 1) * this.pageSize();
    return this.filteredItems().slice(start, start + this.pageSize());
  });
  protected readonly rangeStart = computed(() => this.filteredItems().length ? (this.pages()[this.activeFilter()] - 1) * this.pageSize() + 1 : 0);
  protected readonly rangeEnd = computed(() => Math.min(this.pages()[this.activeFilter()] * this.pageSize(), this.filteredItems().length));
  protected readonly selectedCount = computed(() => this.selectedCodes().size);
  protected readonly selectedVisibleCount = computed(() => this.visibleItems().filter((item) => this.selectedCodes().has(item.code)).length);
  protected readonly allVisibleSelected = computed(() => this.visibleItems().length > 0 && this.visibleItems().every((item) => this.selectedCodes().has(item.code)));
  protected readonly selectedItems = computed(() => PURCHASES_CONFIG.items.filter((item) => this.selectedCodes().has(item.code)));
  protected readonly dryRunItems = computed(() => this.selectedItems().map((item) => ({
    code: item.code,
    name: item.name,
    reason: item.reason,
    quantity: this.quantityFor(item.code),
  })));
  protected readonly orderPriority = computed(() => {
    const selected = this.selectedCodes();
    if (selected.size === 0) return 'sin prioridad';
    if (PURCHASES_CONFIG.items.some((item) => selected.has(item.code) && item.stockGroup === 'out')) return 'urgente';
    if (PURCHASES_CONFIG.items.some((item) => selected.has(item.code) && item.stockGroup === 'low')) return 'bajo mínimo';
    return 'normal';
  });
  protected readonly quantities = signal<Record<string, number>>(Object.fromEntries(
    PURCHASES_CONFIG.items.map((item) => [item.code, item.suggested]),
  ));

  protected isSelected(code: string): boolean {
    return this.selectedCodes().has(code);
  }

  protected countFor(filter: StockFilter): number {
    return PURCHASES_CONFIG.items.filter((item) => item.stockGroup === filter).length;
  }

  protected setFilter(filter: StockFilter): void {
    this.activeFilter.set(filter);
  }

  protected updateSearch(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searches.update((searches) => ({ ...searches, [this.activeFilter()]: value }));
    this.setCurrentPage(1);
  }

  protected setPageSize(event: Event): void {
    this.pageSize.set(Number((event.target as HTMLSelectElement).value) as (typeof PURCHASES_CONFIG.pageSizes)[number]);
    this.pages.set({ out: 1, low: 1, normal: 1 });
  }

  protected setPage(page: number): void {
    this.setCurrentPage(Math.min(Math.max(page, 1), this.pageCount()));
  }

  protected getSearch(filter: StockFilter): string {
    return this.searches()[filter];
  }

  private setCurrentPage(page: number): void {
    this.pages.update((pages) => ({ ...pages, [this.activeFilter()]: page }));
  }

  protected toggleItem(code: string, event: Event): void {
    const selected = new Set(this.selectedCodes());
    if ((event.target as HTMLInputElement).checked) selected.add(code);
    else selected.delete(code);
    this.selectedCodes.set(selected);
  }

  protected toggleAll(event: Event): void {
    const selected = new Set(this.selectedCodes());
    for (const item of this.visibleItems()) {
      if ((event.target as HTMLInputElement).checked) selected.add(item.code);
      else selected.delete(item.code);
    }
    this.selectedCodes.set(selected);
  }

  protected quantityFor(code: string): number {
    return this.quantities()[code] ?? 1;
  }

  protected adjustQuantity(code: string, difference: number): void {
    this.quantities.update((quantities) => ({
      ...quantities,
      [code]: Math.max(1, (quantities[code] ?? 1) + difference),
    }));
  }

  protected openOrderReview(): void {
    this.orderResult.set(null);
    this.orderReviewOpen.set(true);
  }

  protected cancelOrderReview(): void {
    this.orderReviewOpen.set(false);
  }

  private simulationCount = 0;

  protected confirmOrderSimulation(): void {
    this.simulationCount += 1;
    this.orderResult.set({
      code: `SIM-OC-${String(this.simulationCount).padStart(3, '0')}`,
      itemCount: this.selectedCount(),
      priority: this.orderPriority(),
    });
    this.orderReviewOpen.set(false);
  }
}
