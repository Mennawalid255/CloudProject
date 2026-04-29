import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HomeComponent } from './home/home';
import { NavbarComponent } from "./navbar/navbar";
import { SignupComponent } from "./signup/signup";
import { LoginComponent } from "./login/login";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HomeComponent, NavbarComponent, SignupComponent, LoginComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App {
  protected readonly title = signal('CouldProject');

}
