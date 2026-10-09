import { Component } from '@angular/core';
import { FOOTER_CONFIG } from './FOOTER_CONFIG';

@Component({
    selector: 'app-footer',
    standalone: true,
    imports: [],
    templateUrl: './footer.component.html',
})
export class FooterComponent {
    protected readonly config = FOOTER_CONFIG;
}
