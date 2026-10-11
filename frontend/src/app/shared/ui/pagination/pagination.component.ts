import { Component, input, output } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { HlmButtonImports } from '@shared/ui/button';
import { IconComponent } from '@shared/ui/icon';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [HlmButtonImports, IconComponent, DecimalPipe],
  template: `
    <nav class="shared-pagination" aria-label="Paginación">
      <button hlmBtn variant="outline" size="icon-sm" type="button" aria-label="Página anterior"
        [disabled]="page() <= 1" (click)="pageChange.emit(page() - 1)">
        <app-icon name="arrowLeft" class="size-4" />
      </button>
      <span aria-live="polite">{{ page() | number:'2.0-0' }} / {{ pageCount() | number:'2.0-0' }}</span>
      <button hlmBtn variant="outline" size="icon-sm" type="button" aria-label="Página siguiente"
        [disabled]="page() >= pageCount()" (click)="pageChange.emit(page() + 1)">
        <app-icon name="arrowRight" class="size-4" />
      </button>
    </nav>
  `,
  host: { class: 'inline-flex' },
})
export class PaginationComponent {
  readonly page = input.required<number>();
  readonly pageCount = input.required<number>();
  readonly pageChange = output<number>();
}
