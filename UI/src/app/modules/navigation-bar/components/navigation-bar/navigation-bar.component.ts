import {Component, OnInit} from '@angular/core';
import {MenuItem} from 'primeng/api';

@Component({
  selector: 'navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {

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
      {
        label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
          {label: 'About', icon: 'pi pi-fw pi-info'},
          {label: 'Help', icon: 'pi pi-fw pi-question'},
          {label: 'Datasets', icon: 'pi pi-fw pi-save'},
          {label: 'Terms', icon: 'pi pi-fw pi-briefcase'},
        ]
      },
      {
        label: 'Profile', icon: 'pi pi-fw pi-user', items: [
          {label: 'My account', icon: 'pi pi-fw pi-user'},
          {label: 'Logout', icon: 'pi pi-fw pi-sign-out'},
          {label: 'Login', icon: 'pi pi-fw pi-sign-in'},
        ]
      }
    ];
  }

}
