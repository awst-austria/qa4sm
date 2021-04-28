import {Component, OnInit} from '@angular/core';
import {MenuItem} from 'primeng/api';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../../core/services/toast/toast.service';

@Component({
  selector: 'navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {

  items: MenuItem[];
  loginMenuItem: MenuItem;
  logoutMenuItem: MenuItem;
  userProfileMenuItem: MenuItem;

  constructor(private authService: AuthService, private router: Router, private toastService: ToastService) {
    this.loginMenuItem = {label: 'Login', icon: 'pi pi-fw pi-sign-in', routerLink: ['login']};
    this.userProfileMenuItem = {label: 'User profile', icon: 'pi pi-fw pi-user', routerLink: ['user-profile']};
    this.logoutMenuItem = {label: 'Logout', icon: 'pi pi-fw pi-sign-out', command: event => this.logout()};
    this.items = [
      {label: 'Home', icon: 'pi pi-fw pi-home', routerLink: ['']},
      {label: 'Validate', icon: 'pi pi-fw pi-check-square', routerLink: ['validate']},
      {label: 'My validations', icon: 'pi pi-fw pi-folder', routerLink: ['my-validations']},
      {label: 'Published validations', icon: 'pi pi-fw pi-globe', routerLink: ['published-validations']},
      {label: 'Compare validations', icon: 'pi pi-fw pi-th-large', routerLink: ['comparison']},
      {
        label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
          {label: 'About', icon: 'pi pi-fw pi-info', routerLink: ['about']},
          {label: 'Help', icon: 'pi pi-fw pi-question', routerLink: ['help']},
          {label: 'Datasets', icon: 'pi pi-fw pi-save', routerLink: ['datasets']},
          {label: 'Terms', icon: 'pi pi-fw pi-briefcase', routerLink: ['terms']},

        ]
      },
      {
        label: 'Profile', icon: 'pi pi-fw pi-user', items: [
          this.userProfileMenuItem,
          this.logoutMenuItem,
          this.loginMenuItem,
        ]
      }
    ];
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.authStatusChanged(authenticated));
  }

  private authStatusChanged(authenticated: boolean) {
    this.logoutMenuItem.disabled = !authenticated;
    this.loginMenuItem.disabled = authenticated;
    this.userProfileMenuItem.disabled = !authenticated;
  }

  logout() {
    this.authService.logout().subscribe(result => {
        if (result) {//Successful logout
          this.router.navigate(['home']).then(value => this.toastService.showSuccessWithHeader('Logout', 'Successful logout'));
        }
      }
    );
  }

}
