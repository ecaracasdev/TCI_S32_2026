import { Component, inject, signal } from '@angular/core';
import { ToastService, type ToastVariant } from '@core/services/toast.service';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { IconComponent, type UiIconName } from '@shared/ui/icon';
import { PaginationComponent } from '@shared/ui/pagination';
import { DataTableComponent } from '@shared/ui/table';
import { SearchComponent, type SearchFunction } from '@shared/ui/search';

interface SamplePart {
  name: string;
  code: string;
}

@Component({
  selector: 'app-ui-preview-page',
  standalone: true,
  imports: [
    HlmBadgeImports,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    IconComponent,
    PaginationComponent,
    DataTableComponent,
    SearchComponent,
  ],
  templateUrl: './ui-preview.page.html',
  styleUrl: './ui-preview.page.css',
})
export class UiPreviewPage {
  private readonly toastService = inject(ToastService);
  protected readonly toasts = this.toastService.toasts;
  private readonly toastExamples: Record<ToastVariant, { title: string; message: string }> = {
    info: { title: 'Información', message: 'Este es un aviso informativo de ejemplo.' },
    success: { title: 'Operación exitosa', message: 'Los cambios se guardaron correctamente.' },
    warning: { title: 'Atención', message: 'Revisá los datos antes de continuar.' },
    error: { title: 'No se pudo completar', message: 'Ocurrió un error al procesar la solicitud.' },
  };

  protected showToast(variant: ToastVariant): void {
    this.toastService.show({ ...this.toastExamples[variant], variant });
  }

  protected clearToasts(): void {
    this.toastService.clear();
  }

  protected readonly sampleParts: readonly SamplePart[] = [
    { name: 'Filtro de ejemplo', code: 'REP-001' },
    { name: 'Correa de ejemplo', code: 'REP-002' },
    { name: 'Válvula de ejemplo', code: 'REP-003' },
  ];
  protected readonly searchResults = signal(this.sampleParts);
  protected readonly searchParts: SearchFunction<SamplePart> = (collection, term) => {
    const normalizedTerm = term.toLocaleLowerCase('es');
    this.searchResults.set(
      collection.filter(({ name, code }) =>
        `${name} ${code}`.toLocaleLowerCase('es').includes(normalizedTerm),
      ),
    );
  };

  protected readonly colorTokens = [
    { label: 'Fondo', variable: '--ui-background' },
    { label: 'Superficie', variable: '--ui-surface' },
    { label: 'Texto', variable: '--ui-text' },
    { label: 'Primario', variable: '--ui-primary' },
    { label: 'Éxito', variable: '--ui-success' },
    { label: 'Advertencia', variable: '--ui-warning' },
    { label: 'Error', variable: '--ui-danger' },
  ];

  protected readonly icons: UiIconName[] = [
    'activity',
    'alert',
    'boxes',
    'check',
    'factory',
    'location',
    'package',
    'search',
    'shoppingCart',
    'wrench',
  ];
}
