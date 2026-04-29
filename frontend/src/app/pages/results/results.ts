import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.html',
  styleUrl: './results.css',
})
export class Results implements OnInit {

  constructor(public data: DataService) {}

  ngOnInit() {
    if (!this.data.extractedData) {
      const saved = sessionStorage.getItem('invoice');
      if (saved) {
        this.data.extractedData = JSON.parse(saved);
      }
    }
  }
}