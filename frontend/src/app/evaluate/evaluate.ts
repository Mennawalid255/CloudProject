import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-evaluate',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './evaluate.html',
  styleUrls: ['./evaluate.css']
})
export class EvaluateComponent {
  selectedFile: File | null = null;
  result: any = null;
  loading = false;

  constructor(private api: ApiService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  upload() {
    if (!this.selectedFile) {
      alert('Please select a file first');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please login first');
      return;
    }

    this.loading = true;
    this.result = null;

    this.api.upload(this.selectedFile, token).subscribe({
      next: (uploadRes: any) => {
        const filename = uploadRes.file_name;
        if (!filename) {
          alert('Upload failed');
          this.loading = false;
          return;
        }

        this.api.evaluate(filename, token).subscribe({
          next: (res: any) => {
            this.result = res;
            this.loading = false;
            console.log("EVALUATION RESULT:", res);
          },
          error: (err: any) => {
            console.log(err);
            alert('Evaluation failed');
            this.loading = false;
          }
        });
      },
      error: (err: any) => {
        console.log(err);
        alert('Upload failed');
        this.loading = false;
      }
    });
  }

  getF1Color(f1: number): string {
    if (f1 >= 0.8) return 'green';
    if (f1 >= 0.5) return 'orange';
    return 'red';
  }
}

