import {Component, OnInit} from '@angular/core';
import {MenuItem} from 'primeng/api';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Event, NavigationEnd, Router} from '@angular/router';
import {ToastService} from '../../../core/services/toast/toast.service';
import {SettingsService} from '../../../core/services/global/settings.service';

@Component({
  selector: 'navigation-bar-header',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {

  items: MenuItem[];
  homeMenuItem: MenuItem;
  validateMenuItem: MenuItem;
  myResultsMenuItem: MenuItem;
  publishedResultsMenuItem: MenuItem;
  resultsMenuItem: MenuItem;
  compareResultsMenuItem: MenuItem;
  uploadDataMenuItem: MenuItem;
  uploadDataHelpMenuItem: MenuItem;
  datasetUploadMenuItem: MenuItem;
  helpMenuItem: MenuItem;
  userManualMenuItem: MenuItem;
  datasetMenuItem: MenuItem;
  termsMenuItem: MenuItem;
  infoMenuItem: MenuItem;
  contactMenuItem: MenuItem;
  userMenuItem: MenuItem;
  loginMenuItem: MenuItem;
  logoutMenuItem: MenuItem;
  userProfileMenuItem: MenuItem;

  isAuthenticated: boolean;
  currentRoute: string = "";

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService,
              private settingsService: SettingsService) {

    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        this.currentRoute = event.url;
      }
    });

    this.homeMenuItem = {
      label: 'Home',
      icon: 'pi pi-fw pi-home',
      routerLink: ['home'],
      command: () => this.setPreviousUrl('home')
    };

    this.validateMenuItem = {
      label: 'Validate',
      icon: 'pi pi-fw pi-wrench',
      routerLink: ['validate'],
      command: () => this.setPreviousUrl('validate')
    };

    this.myResultsMenuItem = {
      label: 'My validations',
      icon: 'pi pi-fw pi-folder',
      routerLink: ['my-validations']
    };

    this.publishedResultsMenuItem = {
      label: 'Published validations',
      icon: 'pi pi-fw pi-globe',
      routerLink: ['published-validations']
    };

    this.resultsMenuItem = {
      label: 'Results',
      icon: 'pi pi-fw pi-folder',
      items: [
        this.myResultsMenuItem,
        this.publishedResultsMenuItem,
      ]
    };

    this.compareResultsMenuItem = {
      label: 'Compare validations',
      icon: 'pi pi-fw pi-th-large',
      routerLink: ['comparison'],
    };

    this.uploadDataMenuItem = {
      label: 'My datasets',
      icon: 'pi pi-fw pi-upload',
      routerLink: ['my-datasets'],
    };

    this.uploadDataHelpMenuItem = {
      label: 'Upload Data Help',
      icon: 'pi pi-fw pi-question',
      routerLink: ['user-data-guidelines']
    };

    this.datasetUploadMenuItem = {
      label: 'Dataset upload',
      icon: 'pi pi-fw pi-upload',
      items: [
        this.uploadDataHelpMenuItem,
        this.uploadDataMenuItem,
      ]
    };

    this.helpMenuItem = {label: 'Help', icon: 'pi pi-fw pi-question', routerLink: ['help']};
    this.userManualMenuItem = {label: 'User Manual', icon: 'pi pi-fw pi-book', url: '', target: '_blank'}
    this.datasetMenuItem = {label: 'Datasets', icon: 'pi pi-fw pi-save', routerLink: ['datasets']};
    this.termsMenuItem = {label: 'Terms', icon: 'pi pi-fw pi-briefcase', routerLink: ['terms']};
    this.infoMenuItem = {
      label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
        this.helpMenuItem,
        this.userManualMenuItem,
        this.datasetMenuItem,
        this.termsMenuItem,
      ]
    };

    this.contactMenuItem = {label: 'Contact Us', icon: 'pi pi-fw pi-envelope', routerLink: ['contact-us']};

    this.loginMenuItem = {
      label: 'Log in',
      icon: 'pi pi-fw pi-sign-in',
      routerLink: ['login'],
      command: () => this.setPreviousUrl('user-profile'),
      visible: !this.authService.authenticated.value
    };


    this.userProfileMenuItem = {label: 'User profile', icon: 'pi pi-fw pi-user', routerLink: ['user-profile']};
    this.logoutMenuItem = {label: 'Log out', icon: 'pi pi-fw pi-sign-out', command: () => this.logout()};
    this.userMenuItem = {
      label: `My account`,
      icon: 'pi pi-fw pi-user',
      items: [
        this.userProfileMenuItem,
        this.logoutMenuItem,
      ],
    };
  }


  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.authStatusChanged(authenticated));
    this.setSumLink();
  }

  private authStatusChanged(authenticated: boolean): void {
    this.loginMenuItem.visible = !authenticated;
    this.userMenuItem.visible = authenticated;
    this.myResultsMenuItem.visible = authenticated;
    this.compareResultsMenuItem.visible = authenticated;
    this.uploadDataMenuItem.visible = authenticated;
    this.setMenuItems();
  }


  private setMenuItems(): void {
    this.items = [
      this.homeMenuItem,
      this.validateMenuItem,
      this.resultsMenuItem,
      this.datasetUploadMenuItem,
      this.compareResultsMenuItem,
      this.infoMenuItem,
      this.contactMenuItem,
      this.loginMenuItem,
      this.userMenuItem
    ];
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
    const userManualItem = this.items.find(item => item.label === 'Info')
      .items.find(item => item.label === 'User Manual');
    this.settingsService.getAllSettings().subscribe(data => {
      userManualItem.url = data[0].sum_link;
    });
  }

}
