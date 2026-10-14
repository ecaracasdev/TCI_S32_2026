import { Component, input, signal } from '@angular/core';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmInputImports } from '@shared/ui/input';
import { IconComponent } from '@shared/ui/icon';

export type SearchFunction<T> = (collection: readonly T[], term: string) => void;

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [HlmButtonImports, HlmInputImports, IconComponent],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css',
})
export class SearchComponent<T> {
  readonly collection = input.required<readonly T[]>();
  readonly searchFn = input.required<SearchFunction<T>>();
  readonly label = input.required<string>();
  readonly placeholder = input('Buscar...');

  protected readonly query = signal('');

  protected updateQuery(event: Event): void {
    this.query.set((event.target as HTMLInputElement).value);
  }

  protected executeSearch(event: Event): void {
    event.preventDefault();
    this.searchFn()(this.collection(), this.query().trim());
  }
}
