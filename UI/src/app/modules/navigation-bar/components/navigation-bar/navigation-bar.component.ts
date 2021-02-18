import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../../core/services/auth/auth.service';
import {faCoffee} from '@fortawesome/free-solid-svg-icons/faCoffee';
import {faBalanceScale, faDatabase, faDoorOpen, faInfoCircle, faQuestionCircle, faUserCog} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {

  isCollapsed = true;
  aboutIcon=faInfoCircle;
  helpIcon=faQuestionCircle;
  datasetsIcon=faDatabase;
  termsIcon=faBalanceScale;
  profileIcon=faUserCog;
  logoutIcon=faDoorOpen;

  // items: MenuItem[];
  // loginMenuItem: MenuItem;
  // logoutMenuItem: MenuItem;
  // userProfileMenuItem: MenuItem;

  constructor(private authService: AuthService) {
    // this.loginMenuItem = {label: 'Login', icon: 'pi pi-fw pi-sign-in', routerLink: ['login']};
    // this.userProfileMenuItem = {label: 'User profile', icon: 'pi pi-fw pi-user',routerLink:['user-profile']};
    // this.logoutMenuItem = {label: 'Logout', icon: 'pi pi-fw pi-sign-out'};
    // this.items = [
    //   {label: 'Home', icon: 'pi pi-fw pi-home', routerLink: ['']},
    //   {label: 'Validate', icon: 'pi pi-fw pi-check-square', routerLink: ['validate']},
    //   {label: 'My validations', icon: 'pi pi-fw pi-folder'},
    //   {label: 'Published validations', icon: 'pi pi-fw pi-globe'},
    //   {
    //     label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
    //       {label: 'About', icon: 'pi pi-fw pi-info'},
    //       {label: 'Help', icon: 'pi pi-fw pi-question'},
    //       {label: 'Datasets', icon: 'pi pi-fw pi-save'},
    //       {label: 'Terms', icon: 'pi pi-fw pi-briefcase'},
    //     ]
    //   },
    //   {
    //     label: 'Profile', icon: 'pi pi-fw pi-user', items: [
    //       this.userProfileMenuItem,
    //       this.logoutMenuItem,
    //       this.loginMenuItem,
    //     ]
    //   }
    // ];
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.authStatusChanged(authenticated));
  }

  private authStatusChanged(authenticated: boolean) {
    // this.logoutMenuItem.disabled = !authenticated;
    // this.loginMenuItem.disabled = authenticated;
    // this.userProfileMenuItem.disabled = !authenticated;
  }

}
