import { Component } from '@angular/core';
import { ApiService } from '../services/api';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.html',
  styleUrls: ['./home.css'],
})
export class HomeComponent {

  selectedFile: File | null = null;
  result: any = null;

  constructor(private api: ApiService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  upload() {
    console.log("UPLOAD CLICKED");

    if (!this.selectedFile) {
      alert('Please select a file first');
      return;
    }

    const token = localStorage.getItem('token');

    if (!token) {
      alert("No token found. Please login again.");
      return;
    }

    // STEP 1: Upload file
    this.api.upload(this.selectedFile, token).subscribe({
      next: (uploadRes: any) => {

        console.log("UPLOAD RESPONSE:", uploadRes);

        const filename = uploadRes.file_name;

        if (!filename) {
          alert("Filename missing");
          return;
        }

        // STEP 2: Extract data
        this.api.extract(filename, token).subscribe({
          next: (res: any) => {
            console.log("FULL RESPONSE:", res);

            this.result = res.extracted_data.data;

            console.log("RESULT:", this.result);
          },

          error: (err: any) => {
            console.log(err);
            alert('Extraction failed');
          }
        });

      },

      error: (err: any) => {
        console.log(err);
        alert('Upload failed');
      }
    });
  }
}