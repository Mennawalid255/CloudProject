import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router'; // ✅ مهم

@Component({
  selector: 'app-navbar',
  standalone: true,
  templateUrl: './navbar.html',
  styleUrls: ['./navbar.css'],
  imports: [RouterLink] 
})
export class NavbarComponent {

  constructor(private router: Router) {} 
  logout() {
    localStorage.removeItem('user');
    this.router.navigate(['/login']); 
  }
}