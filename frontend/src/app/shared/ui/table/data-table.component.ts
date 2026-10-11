import { Component, input } from '@angular/core';

@Component({
  selector: 'app-data-table',
  standalone: true,
  template: `
    <div class="shared-table-scroll" [style.--shared-table-min-width]="minWidth()">
      <table class="shared-data-table" [class.shared-data-table--stock]="variant() === 'stock'" [class.shared-data-table--machines]="variant() === 'machines'" [class.shared-data-table--purchases]="variant() === 'purchases'"><ng-content /></table>
    </div>
  `,
  host: { class: 'block w-full min-w-0' },
})
export class DataTableComponent {
  readonly minWidth = input('48rem');
  readonly variant = input<'stock' | 'machines' | 'purchases' | 'default'>('default');
}
