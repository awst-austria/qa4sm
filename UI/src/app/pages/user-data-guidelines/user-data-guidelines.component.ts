import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';

@Component({
  selector: 'qa-user-data-guidelines',
  templateUrl: './user-data-guidelines.component.html',
  styleUrls: ['./user-data-guidelines.component.scss']
})
export class UserDataGuidelinesComponent implements OnInit {

  constructor() { }
  @ViewChild('userDataHelpPage') container: ElementRef<HTMLElement>;

  ngOnInit(): void {
  }

}
