import {Component, OnInit} from '@angular/core';

@Component({
  selector: 'qa-user-data-guidelines',
  templateUrl: './user-data-guidelines.component.html',
  styleUrls: ['./user-data-guidelines.component.scss']
})
export class UserDataGuidelinesComponent implements OnInit {
  public pageUrl = '/user-data-guidelines';
  constructor() { }

  ngOnInit(): void {
  }

}
