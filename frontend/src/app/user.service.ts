import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private user: any = JSON.parse(localStorage.getItem('user') || 'null');

  setUser(data: any) {
    this.user = data;
    localStorage.setItem('user', JSON.stringify(data));
  }

  getUser() {
    return this.user;
  }

  updateUser(data: any) {
    this.user = { ...this.user, ...data };
    localStorage.setItem('user', JSON.stringify(this.user));
  }
}