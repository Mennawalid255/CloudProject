import { Component } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private api: ApiService
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  login() {
    console.log("LOGIN CLICKED");
    if (this.form.invalid) return;

    this.api.login(this.form.value).subscribe({
    next: (res: any) => {

      console.log("LOGIN RESPONSE:", res);

      localStorage.setItem('token', res.access_token);

      console.log("TOKEN SAVED:", localStorage.getItem('token'));

      this.router.navigate(['/home']);
    }
    });
  }
}