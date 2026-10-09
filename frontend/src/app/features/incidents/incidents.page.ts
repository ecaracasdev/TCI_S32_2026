import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { IconComponent } from '@shared/ui/icon';
import { UiPreviewDataService } from '@core/services/ui-preview-data.service';

const INCIDENTS_CONFIG = {
  title: 'Reportar incidencia',
  description: 'Contanos qué pasó para que mantenimiento pueda responder cuanto antes.',
  tips: [
    { title: 'Identificá la máquina', text: 'Escaneá el código del equipo o ingresalo manualmente.' },
    { title: 'Agregá una foto', text: 'Una imagen ayuda a entender el problema antes de llegar.' },
    { title: 'Seguimiento inmediato', text: 'El equipo de mantenimiento recibe el aviso al reportar.' },
  ],
};

@Component({
  selector: 'app-incidents-page',
  standalone: true,
  imports: [HlmButtonImports, HlmCardImports, HlmBadgeImports, HlmInputImports, HlmLabelImports, IconComponent],
  templateUrl: './incidents.page.html',
  styleUrl: './incidents.page.css',
})
export class IncidentsPage {
  protected readonly config = INCIDENTS_CONFIG;
  protected readonly submitted = signal(false);
  private readonly machinesPreview = toSignal(inject(UiPreviewDataService).getMachines(), { initialValue: null });
  protected readonly machineCode = signal('FRAC-F02-001');
  protected readonly recentMachines = computed(() => [...(this.machinesPreview()?.items ?? [])]
    .sort((left, right) => this.reviewTimestamp(right.lastReview) - this.reviewTimestamp(left.lastReview))
    .slice(0, 5));
  protected readonly selectedMachine = computed(() => this.machinesPreview()?.items.find(
    (machine) => machine.code.toLowerCase() === this.machineCode().trim().toLowerCase(),
  ) ?? null);

  protected updateMachineCode(event: Event): void {
    this.machineCode.set((event.target as HTMLInputElement).value);
  }

  protected submit(event: Event): void {
    event.preventDefault();
    this.submitted.set(true);
  }

  protected newReport(): void {
    this.submitted.set(false);
  }

  private reviewTimestamp(value: string): number {
    const match = value.match(/(Hoy|Ayer),\s*(\d{2}):(\d{2})/i);
    if (!match) return Number.MIN_SAFE_INTEGER;
    const day = match[1].toLowerCase() === 'hoy' ? 2 : 1;
    return day * 1440 + Number(match[2]) * 60 + Number(match[3]);
  }
}
