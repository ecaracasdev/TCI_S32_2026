import { DecimalPipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { IconComponent } from '@shared/ui/icon';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';

const UI_PREVIEW_CONFIG = {
  eyebrow: 'OPERACIÓN DE PLANTA · MUESTRA VISUAL',
  title: 'Vista general',
  description: 'Un panorama rápido del estado de las máquinas, las incidencias y los repuestos de la planta.',
  notice: 'Datos de demostración',
  chartTitle: 'Incidencias por estado',
  chartDescription: 'Distribución de los reportes incluidos en la muestra.',
  actionsTitle: 'Botones de acción',
  actionsDescription: 'Variantes visuales disponibles para las acciones de la aplicación.',
  primaryLabel: 'Primario',
  primaryAction: 'Reportar incidencia',
  secondaryLabel: 'Secundario',
  secondaryAction: 'Ver inventario',
  outlineLabel: 'Contorno',
  outlineAction: 'Lista de compras',
};

@Component({
  selector: 'app-ui-preview-page',
  standalone: true,
  imports: [RouterLink, HlmBadgeImports, HlmButtonImports, HlmCardImports, IconComponent, DecimalPipe],
  templateUrl: './ui-preview.page.html',
  styleUrl: './ui-preview.page.css',
})
export class UiPreviewPage {
  protected readonly config = UI_PREVIEW_CONFIG;
  protected readonly preview = toSignal(inject(UiPreviewDataService).getGeneralPreview(), { initialValue: null });

  protected readonly metrics = computed(() => {
    const data = this.preview();
    if (!data) return null;

    const machines = data.machines.items;
    const parts = data.stock.items;
    const incidentStates = [...new Set(data.dashboard.incidents.map((incident) => incident.state))]
      .map((state) => ({
        label: state,
        count: data.dashboard.incidents.filter((incident) => incident.state === state).length,
        tone: data.dashboard.incidents.find((incident) => incident.state === state)?.tone ?? 'info',
      }));
    return {
      machineCount: machines.length,
      operationalMachines: machines.filter((machine) => machine.status === 'Operativa').length,
      openIncidents: data.dashboard.incidents.length,
      noStockParts: parts.filter((part) => part.physical === 0).length,
      restockParts: parts.filter((part) => part.physical <= part.minimum).length,
      machines,
      incidents: data.dashboard.incidents,
      incidentStates,
      incidentChartLabel: incidentStates.map((state) => `${state.label}, ${state.count}`).join('; '),
      parts: parts.filter((part) => part.physical <= part.minimum),
      stockCounts: {
        empty: parts.filter((part) => part.physical === 0).length,
        low: parts.filter((part) => part.physical > 0 && part.physical <= part.minimum).length,
        available: parts.filter((part) => part.physical > part.minimum).length,
      },
    };
  });
}
