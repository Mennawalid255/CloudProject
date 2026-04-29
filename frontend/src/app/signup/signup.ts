import { Component } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './signup.html',
  styleUrls: ['./signup.css']
})
export class SignupComponent {

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private apiService: ApiService
  ) {
    this.form = this.fb.group({
      firstName: [''],
      lastName: [''],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    });
  }

  signup() {
    if (this.form.invalid) return;

    const { email, password, confirmPassword } = this.form.value;

    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

this.apiService.register({
  email,
  password
}).subscribe({
  next: (res: any) => {
    alert("Registered successfully");
    this.router.navigate(['/login']);
  },
  error: (err: any) => {
    console.log(err);
    alert("Registration failed");
  }
});
  }
}
