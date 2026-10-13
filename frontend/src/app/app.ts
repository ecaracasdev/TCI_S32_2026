import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './shared/header/header.component';
import { FooterComponent } from "@shared/footer/footer.component";
import { ToastContainerComponent } from '@shared/ui/toast';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HeaderComponent, FooterComponent, ToastContainerComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
}
