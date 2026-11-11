import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@shared/ui/button';
import { HlmCardImports } from '@shared/ui/card';
import { EN_DESARROLLO_CONFIG } from './en-desarrollo.config';

@Component({
  selector: 'app-en-desarrollo-page',
  standalone: true,
  imports: [RouterLink, HlmButtonImports, HlmCardImports],
  templateUrl: './en-desarrollo.page.html',
})
export class EnDesarrolloPage {
  protected readonly config = EN_DESARROLLO_CONFIG;
}
