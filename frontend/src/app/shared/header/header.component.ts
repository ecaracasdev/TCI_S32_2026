import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { IconComponent } from '@shared/ui/icon';
import { HEADER_CONFIG } from './HEADER_CONFIG';

type UserRole = typeof HEADER_CONFIG.roles[number];

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, IconComponent],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
})
export class HeaderComponent {
  protected readonly config = HEADER_CONFIG;
  protected readonly activeRole = signal<UserRole>(HEADER_CONFIG.roles[0]);
  protected readonly isRoleMenuOpen = signal(false);
  protected readonly isMoreMenuOpen = signal(false);
  private holdTimer: ReturnType<typeof setTimeout> | undefined;
  private suppressRoleClick = false;

  protected startRoleHold(): void {
    this.clearHoldTimer();
    this.suppressRoleClick = false;
    this.holdTimer = setTimeout(() => {
      this.suppressRoleClick = true;
      this.isRoleMenuOpen.set(true);
      this.isMoreMenuOpen.set(false);
    }, 480);
  }

  protected endRoleHold(): void {
    this.clearHoldTimer();
    if (this.suppressRoleClick) {
      setTimeout(() => this.suppressRoleClick = false, 0);
    }
  }

  protected toggleRoleMenu(): void {
    if (this.suppressRoleClick) {
      this.suppressRoleClick = false;
      return;
    }
    this.isRoleMenuOpen.update((open) => !open);
    this.isMoreMenuOpen.set(false);
  }

  protected toggleMoreMenu(): void {
    this.isMoreMenuOpen.update((open) => !open);
    this.isRoleMenuOpen.set(false);
  }

  protected selectRole(role: UserRole): void {
    this.activeRole.set(role);
    this.closeMenus();
  }

  protected closeMenus(): void {
    this.isRoleMenuOpen.set(false);
    this.isMoreMenuOpen.set(false);
  }

  private clearHoldTimer(): void {
    if (this.holdTimer !== undefined) {
      clearTimeout(this.holdTimer);
      this.holdTimer = undefined;
    }
  }
}
