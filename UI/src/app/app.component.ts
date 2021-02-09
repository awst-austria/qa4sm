import {Component, OnInit} from '@angular/core';
import {MenubarModule} from 'primeng/menubar';
import {MenuItem} from 'primeng/api';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
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
      {label: 'Info', icon: 'pi pi-fw pi-info-circle', routerLink: ['validate'], items: [
          {label: 'About', icon: 'pi pi-fw pi-info'},
          {label: 'Help', icon: 'pi pi-fw pi-question'},
          {label: 'Datasets', icon: 'pi pi-fw pi-save'},
          {label: 'Terms', icon: 'pi pi-fw pi-briefcase'},
        ]},
      {label: 'Profile', icon: 'pi pi-fw pi-user',items:[
          {label: 'My account', icon: 'pi pi-fw pi-user'},
          {label: 'Logout', icon: 'pi pi-fw pi-sign-out'},
          {label: 'Login', icon: 'pi pi-fw pi-sign-in'},
        ]}
    ];
  }
}
