import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';
import { DataService } from '../../services/data.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrl: './upload.css'
})
export class UploadComponent {

  selectedFile!: File;

  constructor(
    private api: ApiService,
    public data: DataService,
    private router: Router
  ) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    if (!this.selectedFile) {
      alert("Please choose a file");
      return;
    }

    const token = localStorage.getItem('token');

    if (!token) {
      alert("You are not logged in. Please login again.");
      return;
    }

    this.api.upload(this.selectedFile, token).subscribe({
      next: (res: any) => {

        const filename = res?.file_name;

        if (!filename) {
          alert("Upload succeeded but filename missing");
          return;
        }

        this.extractFile(filename);
      },

      error: (err: any) => {
        console.log("UPLOAD ERROR:", err);
        alert("Upload failed");
      }
    });
  }

  extractFile(filename: string) {
    const token = localStorage.getItem('token');

    if (!token) return;

    this.api.extract(filename, token).subscribe({
      next: (res: any) => {

        const data = res?.extracted_data?.data;

        if (!data) {
          console.log("No extracted data returned");
          return;
        }

        // ✅ 1. Save in service (live UI)
        this.data.extractedData = { ...data };

        // ✅ 2. Save in sessionStorage (persistent)
        sessionStorage.setItem('invoice', JSON.stringify(data));

        console.log("FULL RESPONSE:", res);
        console.log("EXTRACTED:", data);

        // ✅ 3. Navigate to results
        this.router.navigate(['/results']);
      },

      error: (err: any) => {
        console.log("EXTRACT ERROR:", err);
      }
    });
  }
}