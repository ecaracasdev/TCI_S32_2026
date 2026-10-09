import { Directive, input } from '@angular/core';
import { classes } from '@shared/ui/utils';
import { HlmCardConfig, injectHlmCardConfig } from './hlm-card.token';

@Directive({
	selector: '[hlmCard],hlm-card',
	host: {
		'data-slot': 'card',
		'[attr.data-size]': 'size()',
	},
})
export class HlmCard {
	private readonly _defaultConfig = injectHlmCardConfig();
	public readonly size = input<HlmCardConfig['size']>(this._defaultConfig.size);

	constructor() {
		classes(() => 'border border-border bg-card text-card-foreground gap-(--card-spacing) overflow-hidden rounded-lg py-(--card-spacing) text-sm shadow-none [--card-spacing:--spacing(6)] has-[>img:first-child]:pt-0 data-[size=sm]:[--card-spacing:--spacing(4)] *:[img:first-child]:rounded-lg *:[img:last-child]:rounded-lg group/card flex flex-col');
	}
}
