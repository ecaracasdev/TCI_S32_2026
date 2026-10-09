import { Component, computed, input } from '@angular/core';
import { NgIcon, type IconType } from '@ng-icons/core';
import { UI_ICON_NAMES, type UiIconName } from './icons';

@Component({
  selector: 'app-icon',
  standalone: true,
  imports: [NgIcon],
  template: '<ng-icon class="inline-flex size-full" [name]="iconName()" aria-hidden="true" />',
  host: { class: 'inline-flex shrink-0 items-center justify-center align-middle' },
})
export class IconComponent {
  readonly name = input.required<UiIconName>();
  protected readonly iconName = computed<IconType>(() => UI_ICON_NAMES[this.name()]);
}
