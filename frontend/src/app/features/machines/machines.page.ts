import { Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { IconComponent } from '@shared/ui/icon';
import { DataTableComponent } from '@shared/ui/table';
import { PaginationComponent } from '@shared/ui/pagination';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';

type MachineFilter = 'Todas' | 'Con incidencias' | 'Operativas';

const MACHINES_CONFIG = {
  title: 'Estado de máquinas',
  description: 'Consultá la condición de los equipos y las incidencias asociadas en los tres turnos.',
  filters: ['Todas', 'Con incidencias', 'Operativas'] as const,
};

@Component({
  selector: 'app-machines-page',
  standalone: true,
  imports: [HlmButtonImports, HlmCardImports, HlmBadgeImports, IconComponent, DataTableComponent, PaginationComponent, DecimalPipe],
  templateUrl: './machines.page.html',
  styleUrl: './machines.page.css',
})
export class MachinesPage {
  protected readonly config = MACHINES_CONFIG;
  protected readonly preview = toSignal(inject(UiPreviewDataService).getMachines(), { initialValue: null });
  protected readonly selectedFilter = signal<MachineFilter>('Todas');
  protected readonly page = signal(1);
  private readonly pageSize = 5;
  protected readonly filteredMachines = computed(() => {
    const filter = this.selectedFilter();
    const machines = this.preview()?.items ?? [];
    return machines.filter((machine) => filter === 'Todas' || (filter === 'Con incidencias' ? machine.incidents > 0 : machine.status === 'Operativa'));
  });
  protected readonly pageCount = computed(() => Math.max(1, Math.ceil(this.filteredMachines().length / this.pageSize)));
  protected readonly visibleMachines = computed(() => this.filteredMachines().slice((this.page() - 1) * this.pageSize, this.page() * this.pageSize));
  protected readonly rangeStart = computed(() => this.filteredMachines().length === 0 ? 0 : (this.page() - 1) * this.pageSize + 1);
  protected readonly rangeEnd = computed(() => Math.min(this.page() * this.pageSize, this.filteredMachines().length));

  protected setFilter(filter: MachineFilter): void {
    this.selectedFilter.set(filter);
    this.page.set(1);
  }

  protected setPage(page: number): void {
    this.page.set(Math.min(Math.max(page, 1), this.pageCount()));
  }
}
