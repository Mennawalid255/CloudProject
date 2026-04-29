import { Component } from '@angular/core';
import { UserService } from '../user.service';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-edit',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './edit.html',
  styleUrls: ['./edit.css']
})
export class EditComponent {

  user: any;

  constructor(private userService: UserService, private router: Router) {
    this.user = { ...this.userService.getUser() };
  }

  save() {
    this.userService.updateUser(this.user);
    this.router.navigate(['/profile']);
  }
}