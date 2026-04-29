import { Component } from '@angular/core';
import { UserService } from '../user.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css']
})
export class ProfileComponent {

  user: any;

  constructor(private userService: UserService) {
    this.user = this.userService.getUser();
  }
}