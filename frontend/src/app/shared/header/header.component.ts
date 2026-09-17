import { Component, signal } from '@angular/core';
import { HEADER_CONFIG } from './HEADER_CONFIG';

@Component({
    selector: 'app-header',
    standalone: true,
    imports: [],
    templateUrl: './header.component.html',
    styleUrl: './header.component.css',
})
export class HeaderComponent {
    protected readonly config = HEADER_CONFIG;
    protected readonly isMenuOpen = signal(false);

    protected toggleMenu(): void {
        this.isMenuOpen.update((current) => !current);
    }

    protected closeMenu(): void {
        this.isMenuOpen.set(false);
    }
}
