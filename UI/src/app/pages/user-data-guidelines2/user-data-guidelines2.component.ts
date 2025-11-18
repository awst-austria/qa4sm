import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
    selector: 'qa-user-data-guidelines2',
    imports: [CommonModule, RouterLink],
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
   copy(id: string) {
    const el = document.getElementById(id) as HTMLTextAreaElement | null;
    if (!el) return;
    el.select();
    el.setSelectionRange(0, el.value.length);
    navigator.clipboard?.writeText(el.value);
  }
  
}