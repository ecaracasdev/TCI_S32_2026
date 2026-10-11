import { Component } from '@angular/core';
import { HlmBadgeImports } from '@shared/ui/badge';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { HlmInputImports } from '@shared/ui/input';
import { HlmLabelImports } from '@shared/ui/label';
import { IconComponent, type UiIconName } from '@shared/ui/icon';
import { PaginationComponent } from '@shared/ui/pagination';
import { DataTableComponent } from '@shared/ui/table';

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
  ],
  templateUrl: './ui-preview.page.html',
  styleUrl: './ui-preview.page.css',
})
export class UiPreviewPage {
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
