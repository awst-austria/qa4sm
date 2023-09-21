import {Component, OnInit} from '@angular/core';
import {MenuItem} from 'primeng/api';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../../core/services/toast/toast.service';
import {SettingsService} from '../../../core/services/global/settings.service';
import {BehaviorSubject} from 'rxjs';

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
  isFixed: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(true);

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService,
              private settingsService: SettingsService) {

    this.loginMenuItem = {
      label: 'Log in',
      icon: 'pi pi-fw pi-sign-in',
      routerLink: ['login'],
      command: () => this.setPreviousUrl('user-profile')
    };
    this.userProfileMenuItem = {label: 'User profile', icon: 'pi pi-fw pi-user', routerLink: ['user-profile']};
    this.logoutMenuItem = {label: 'Log out', icon: 'pi pi-fw pi-sign-out', command: () => this.logout()};
    this.items = [
      {label: 'Home', icon: 'pi pi-fw pi-home', routerLink: ['home'], command: () => this.setPreviousUrl('home')},
      {
        label: 'Validate',
        icon: 'pi pi-fw pi-wrench',
        routerLink: ['validate'],
        // styleClass: 'validate-button',
        command: () => this.setPreviousUrl('validate')
      },
      {
        label: 'Results',
        icon: 'pi pi-fw pi-folder',
        items: [
          {
            label: 'My validations',
            icon: 'pi pi-fw pi-folder',
            routerLink: ['my-validations'],
            command: () => this.setPreviousUrl('my-validations')
          },
          {label: 'Published validations', icon: 'pi pi-fw pi-globe', routerLink: ['published-validations']},
        ]
      },
      {label: 'Compare validations', icon: 'pi pi-fw pi-th-large', routerLink: ['comparison'], command: () => this.setPreviousUrl('comparison')},
      {
        label: 'Dataset upload',
        icon: 'pi pi-fw pi-upload',
        items: [
          {label: 'My datasets',
            icon: 'pi pi-fw pi-upload',
            routerLink: ['my-datasets'],
            command: () => this.setPreviousUrl('my-datasets')
          },
          {label: 'Upload Data Help', icon: 'pi pi-fw pi-question', routerLink: ['user-data-guidelines']},
        ]
      },

      {
        label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
          // {label: 'About', icon: 'pi pi-fw pi-info', routerLink: ['about']},
          {label: 'Help', icon: 'pi pi-fw pi-question', routerLink: ['help']},
          {
            label: 'User Manual',
            icon: 'pi pi-fw pi-book',
            url: '',
            target: '_blank'
          },
          {label: 'Datasets', icon: 'pi pi-fw pi-save', routerLink: ['datasets']},
          {label: 'Terms', icon: 'pi pi-fw pi-briefcase', routerLink: ['terms']},
        ]
      },
      {label: 'Contact Us', icon: 'pi pi-fw pi-envelope', routerLink: ['contact-us']},
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
    this.setSumLink();
  }

  private authStatusChanged(authenticated: boolean): void {
    this.logoutMenuItem.disabled = !authenticated;
    this.loginMenuItem.disabled = authenticated;
    this.userProfileMenuItem.disabled = !authenticated;
  }

  logout(): void {
    this.authService.logout().subscribe(result => {
        this.setPreviousUrl('');
        if (result) {// Successful logout
          this.router.navigate(['home']).then(() => this.toastService.showSuccessWithHeader('Logout', 'Successful logout'));
        }
      }
    );
  }

  setPreviousUrl(prevUrl: string): void {
    this.authService.setPreviousUrl(prevUrl);
  }

  setSumLink(): void {
    const userManualItem =  this.items.find(item => item.label === 'Info')
      .items.find(item => item.label === 'User Manual');
    this.settingsService.getAllSettings().subscribe(data => {
      userManualItem.url = data[0].sum_link;
    });
  }

}
