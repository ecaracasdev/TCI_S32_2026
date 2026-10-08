import { Component, computed, signal } from '@angular/core';

const MACHINES_CONFIG = {
  title: 'Estado de máquinas',
  description: 'Consultá la condición de los equipos y las incidencias asociadas en los tres turnos.',
  machines: [
    { code: 'CAL-C01-001', name: 'Caldera C-01', type: 'Caldera de vapor', sector: 'Servicios auxiliares', status: 'En reparación', tone: 'danger', incidents: 1, lastReview: 'Hoy, 07:32', icon: '♨' },
    { code: 'FRAC-F02-001', name: 'Fraccionador F-02', type: 'Línea de fraccionado', sector: 'Envasado · Línea 2', status: 'En triage', tone: 'warning', incidents: 1, lastReview: 'Hoy, 08:30', icon: '◉' },
    { code: 'BAND-B04-001', name: 'Banda transportadora B-04', type: 'Transportador modular', sector: 'Envasado · Línea 4', status: 'En reparación', tone: 'info', incidents: 1, lastReview: 'Hoy, 08:05', icon: '⇢' },
    { code: 'CAL-C02-001', name: 'Caldera C-02', type: 'Caldera de vapor', sector: 'Servicios auxiliares', status: 'Operativa', tone: 'good', incidents: 0, lastReview: 'Ayer, 22:10', icon: '♨' },
    { code: 'FRAC-F01-001', name: 'Fraccionador F-01', type: 'Línea de fraccionado', sector: 'Envasado · Línea 1', status: 'Operativa', tone: 'good', incidents: 0, lastReview: 'Ayer, 18:45', icon: '◉' },
    { code: 'BAND-B02-001', name: 'Banda transportadora B-02', type: 'Transportador modular', sector: 'Envasado · Línea 2', status: 'Operativa', tone: 'good', incidents: 0, lastReview: 'Ayer, 16:22', icon: '⇢' },
  ],
};

@Component({
  selector: 'app-machines-page',
  standalone: true,
  templateUrl: './machines.page.html',
  styleUrl: './machines.page.css',
})
export class MachinesPage {
  protected readonly config = MACHINES_CONFIG;
  protected readonly selectedFilter = signal('Todas');
  protected readonly visibleMachines = computed(() => {
    const filter = this.selectedFilter();
    return this.config.machines.filter((machine) => filter === 'Todas' || (filter === 'Con incidencias' ? machine.incidents > 0 : machine.status === 'Operativa'));
  });

  protected setFilter(filter: string): void {
    this.selectedFilter.set(filter);
  }
}
