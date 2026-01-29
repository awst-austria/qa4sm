import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
    selector: 'qa-user-data-guidelines',
    imports: [CommonModule, RouterLink],
    templateUrl: './user-data-guidelines.component.html',
    styleUrls: ['./user-data-guidelines.component.scss']
})


export class UserDataGuidelinesComponent implements OnInit {
  currentPage!: string;

  ngOnInit() {
    this.currentPage = 'info';  // Set default page
  }

  switchPage(page: string) {
    this.currentPage = page;
  }
   copy(id: string) {
    const el = document.getElementById(id) as HTMLTextAreaElement | null;
    if (!el) return;
    el.select();
    el.setSelectionRange(0, el.value.length);
    navigator.clipboard?.writeText(el.value);
  }
  
}