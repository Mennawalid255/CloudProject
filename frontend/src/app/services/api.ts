import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  register(data: any) {
    return this.http.post(`${this.baseUrl}/register`, data);
  }
  
  login(data: any) {
    return this.http.post(`${this.baseUrl}/login`, data);
  }

  upload(file: File, token: string) {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(
      `${this.baseUrl}/upload/`,
      formData,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  extract(filename: string, token: string) {
    return this.http.get(
      `${this.baseUrl}/extract/${filename}`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }
}
