import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'qa-user-data-guidelines2',
  standalone: true, 
  imports: [CommonModule, RouterOutlet],
  templateUrl: './user-data-guidelines2.component.html',
  styleUrls: ['./user-data-guidelines2.component.scss']
})


export class UserDataGuidelinesComponent2 implements OnInit {
  currentPage!: string;

  ngOnInit() {
    this.currentPage = 'info';  // Set default page
  }

  switchPage(page: string) {
    this.currentPage = page;
  }
}