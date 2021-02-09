import {Component, OnInit} from '@angular/core';
import {MenubarModule} from 'primeng/menubar';
import {MenuItem} from 'primeng/api';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{
  title = 'qa4sm-ui';
  items: MenuItem[];

  constructor() {
    this.items = [];
  }

  ngOnInit(): void {
    this.items = [
      {label: 'Home', icon: 'pi pi-fw pi-home', routerLink: ['']},
      {label: 'Validate', icon: 'pi pi-fw pi-check-square', routerLink: ['validate']},
      {label: 'My validations', icon: 'pi pi-fw pi-folder'},
      {label: 'Published validations', icon: 'pi pi-fw pi-globe'},
      {label: 'Profile', icon: 'pi pi-fw pi-user'}
    ];
  }
}
