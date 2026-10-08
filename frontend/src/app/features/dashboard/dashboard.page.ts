import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

const DASHBOARD_CONFIG = {
  greeting: 'Buen día, Nicolás',
  description: 'Así está la operación de mantenimiento en este momento.',
  metrics: [
    { label: 'Incidencias activas', value: '08', note: '3 requieren atención', tone: 'danger', icon: '↗' },
    { label: 'Repuestos bajo mínimo', value: '12', note: 'En lista de compras', tone: 'warning', icon: '⌁' },
    { label: 'Máquinas operativas', value: '94%', note: '2 fuera de servicio', tone: 'good', icon: '◉' },
    { label: 'Reparaciones hoy', value: '06', note: '4 completadas', tone: 'info', icon: '✓' },
  ],
  incidents: [
    { code: 'INC-0248', machine: 'Fraccionador F-02', issue: 'Vibración anormal en motor', time: 'Hace 12 min', state: 'En triage', tone: 'warning', initials: 'LM' },
    { code: 'INC-0247', machine: 'Banda transportadora B-04', issue: 'Desalineación de banda', time: 'Hace 38 min', state: 'En reparación', tone: 'info', initials: 'CR' },
    { code: 'INC-0246', machine: 'Caldera C-01', issue: 'Fuga en válvula de presión', time: 'Hace 1 h', state: 'Urgente', tone: 'danger', initials: 'AP' },
  ],
  stock: [
    { name: 'Rodamiento 6205-2RS', code: 'REP-00142', count: '2 u.', min: 'Mín. 5', tone: 'danger', location: 'A-03-12' },
    { name: 'Filtro de aceite FO-18', code: 'REP-00087', count: '4 u.', min: 'Mín. 6', tone: 'warning', location: 'B-01-04' },
    { name: 'Correa dentada HTD-8M', code: 'REP-00203', count: '1 u.', min: 'Mín. 3', tone: 'danger', location: 'A-02-08' },
  ],
};

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './dashboard.page.html',
  styleUrl: './dashboard.page.css',
})
export class DashboardPage {
  protected readonly config = DASHBOARD_CONFIG;
}
