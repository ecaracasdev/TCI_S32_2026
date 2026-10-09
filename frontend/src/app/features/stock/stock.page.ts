import { Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmInputImports } from '@shared/ui/input';
import { IconComponent } from '@shared/ui/icon';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';
import { DataTableComponent } from '@shared/ui/table';
import { PaginationComponent } from '@shared/ui/pagination';

const STOCK_CONFIG = {
  title: 'Inventario de repuestos',
  description: 'Consultá existencias, disponibilidad y ubicación de cada repuesto en el almacén.',
  filters: [
    { value: 'all', label: 'Todos' },
    { value: 'out', label: 'Sin stock' },
    { value: 'low', label: 'Bajo mínimo' },
    { value: 'normal', label: 'Stock normal' },
  ] as const,
};

type StockFilter = typeof STOCK_CONFIG.filters[number]['value'];

@Component({
  selector: 'app-stock-page',
  standalone: true,
  imports: [HlmButtonImports, HlmCardImports, HlmBadgeImports, HlmInputImports, IconComponent, DecimalPipe, DataTableComponent, PaginationComponent],
  templateUrl: './stock.page.html',
  styleUrl: './stock.page.css',
})
export class StockPage {
  protected readonly config = STOCK_CONFIG;
  protected readonly preview = toSignal(inject(UiPreviewDataService).getStock(), { initialValue: null });
  protected readonly query = signal('');
  protected readonly activeFilter = signal<StockFilter>('all');
  protected readonly page = signal(1);
  private readonly pageSize = 5;
  protected readonly filteredItems = computed(() => {
    const term = this.query().trim().toLocaleLowerCase('es');
    return (this.preview()?.items ?? []).filter((item) => {
      const matchesText = !term || `${item.code} ${item.name} ${item.description} ${item.machines} ${item.location}`.toLocaleLowerCase('es').includes(term);
      const available = item.physical - item.reserved;
      const filter = this.activeFilter();
      const matchesFilter = filter === 'all'
        || (filter === 'out' && available <= 0)
        || (filter === 'low' && available > 0 && available <= item.minimum)
        || (filter === 'normal' && available > item.minimum);
      return matchesText && matchesFilter;
    });
  });
  protected readonly pageCount = computed(() => Math.max(1, Math.ceil(this.filteredItems().length / this.pageSize)));
  protected readonly visibleItems = computed(() => this.filteredItems().slice((this.page() - 1) * this.pageSize, this.page() * this.pageSize));
  protected readonly rangeStart = computed(() => this.filteredItems().length === 0 ? 0 : (this.page() - 1) * this.pageSize + 1);
  protected readonly rangeEnd = computed(() => Math.min(this.page() * this.pageSize, this.filteredItems().length));

  protected updateQuery(event: Event): void {
    this.query.set((event.target as HTMLInputElement).value);
    this.page.set(1);
  }

  protected countFor(filter: StockFilter): number {
    const items = this.preview()?.items ?? [];
    if (filter === 'all') return items.length;
    return items.filter((item) => {
      const available = item.physical - item.reserved;
      return filter === 'out' ? available <= 0
        : filter === 'low' ? available > 0 && available <= item.minimum
        : available > item.minimum;
    }).length;
  }

  protected setFilter(filter: StockFilter): void {
    this.activeFilter.set(filter);
    this.page.set(1);
  }

  protected setPage(page: number): void {
    this.page.set(Math.min(Math.max(page, 1), this.pageCount()));
  }
}
