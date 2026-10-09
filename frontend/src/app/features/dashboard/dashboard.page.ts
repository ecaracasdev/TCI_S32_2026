import { Component, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { IconComponent } from '@shared/ui/icon';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';

const DASHBOARD_CONFIG = {
  greeting: 'Inicio del sistema',
  description: 'Accedé rápidamente a las tareas de mantenimiento de la planta.',
  primaryAction: 'Reportar incidencia',
  reviewAction: 'Revisar lista de compras',
};

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [RouterLink, HlmButtonImports, HlmCardImports, HlmBadgeImports, IconComponent, DecimalPipe],
  templateUrl: './dashboard.page.html',
  styleUrl: './dashboard.page.css',
})
export class DashboardPage {
  protected readonly config = DASHBOARD_CONFIG;
  protected readonly preview = toSignal(inject(UiPreviewDataService).getDashboard(), { initialValue: null });
}
