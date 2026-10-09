import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideIcons } from '@ng-icons/core';

import { routes } from './app.routes';
import { UI_ICON_SET } from './shared/ui/icon';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(),
    provideIcons(UI_ICON_SET),
  ]
};
