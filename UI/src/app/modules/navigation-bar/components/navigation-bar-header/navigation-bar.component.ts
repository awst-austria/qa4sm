import {Component, HostListener, OnInit, signal} from '@angular/core';
import {MenuItem} from 'primeng/api';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Event, NavigationEnd, Router} from '@angular/router';
import {ToastService} from '../../../core/services/toast/toast.service';
import {SettingsService} from '../../../core/services/global/settings.service';

@Component({
  selector: 'qa-navigation-bar-header',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {
  isMaintenancePossible = false;
  potentialMaintenanceDescription = '';

  items: MenuItem[];
  homeMenuItem: MenuItem = {
    label: 'Home',
    icon: 'pi pi-fw pi-home',
    routerLink: ['home'],
    command: () => this.setPreviousUrl('home')
  };
  validateMenuItem: MenuItem = {
    label: 'Validate',
    icon: 'pi pi-fw pi-wrench',
    routerLink: ['validate'],
    command: () => this.setPreviousUrl('validate')
  };
  myResultsMenuItem: MenuItem = {
    label: 'My validations',
    icon: 'pi pi-fw pi-folder',
    routerLink: ['my-validations']
  };
  publishedResultsMenuItem: MenuItem = {
    label: 'Published validations',
    icon: 'pi pi-fw pi-globe',
    routerLink: ['published-validations']
  };
  resultsMenuItem: MenuItem = {
    label: 'Results',
    icon: 'pi pi-fw pi-folder',
    items: [
      this.myResultsMenuItem,
      this.publishedResultsMenuItem,
    ]
  };
  compareResultsMenuItem: MenuItem = {
    label: 'Compare validations',
    icon: 'pi pi-fw pi-th-large',
    routerLink: ['comparison'],
  };
  uploadDataMenuItem: MenuItem = {
    label: 'My datasets',
    icon: 'pi pi-fw pi-upload',
    routerLink: ['my-datasets'],
  };

  uploadDataHelpMenuItem: MenuItem = {
    label: 'Data Preparation',
    icon: 'pi pi-fw pi-question',
    routerLink: ['user-data-guidelines']
  };

  datasetUploadMenuItem: MenuItem = {
    label: 'Dataset upload',
    icon: 'pi pi-fw pi-upload',
    items: [
      this.uploadDataHelpMenuItem,
      this.uploadDataMenuItem,
    ]
  };

  helpMenuItem: MenuItem = {label: 'Help', icon: 'pi pi-fw pi-question', routerLink: ['help']};
  userManualMenuItem: MenuItem = {label: 'User Manual', icon: 'pi pi-fw pi-book', url: '', target: '_blank'}
  datasetMenuItem: MenuItem = {label: 'Datasets', icon: 'pi pi-fw pi-save', routerLink: ['datasets']};
  termsMenuItem: MenuItem = {label: 'Terms', icon: 'pi pi-fw pi-briefcase', routerLink: ['terms']};
  infoMenuItem: MenuItem = {
    label: 'Info', icon: 'pi pi-fw pi-info-circle', items: [
      this.helpMenuItem,
      this.userManualMenuItem,
      this.datasetMenuItem,
      this.termsMenuItem,
    ]
  };
  contactMenuItem: MenuItem = {label: 'Contact Us', icon: 'pi pi-fw pi-envelope', routerLink: ['contact-us']};

  loginMenuItem: MenuItem = {
    label: 'Log in',
    icon: 'pi pi-fw pi-sign-in',
    routerLink: ['login'],
    command: () => this.setPreviousUrl('user-profile'),
    visible: !this.authService.authenticated.value
  };

  logoutMenuItem: MenuItem = {label: 'Log out', icon: 'pi pi-fw pi-sign-out', command: () => this.logout()};
  userProfileMenuItem: MenuItem = {label: 'User profile', icon: 'pi pi-fw pi-user', routerLink: ['user-profile']};

  userMenuItem: MenuItem = {
    label: `My account`,
    icon: 'pi pi-fw pi-user',
    items: [
      this.userProfileMenuItem,
      this.logoutMenuItem,
    ],
  };

  isAuthenticated: boolean;
  isHomePage = signal<boolean | undefined>(undefined)
  isLogoDisplayed = signal<boolean>(true)

  longLogo: Logo = {path:  '/static/images/logo/qa4sm_logo_long.webp', height: '45', shape: 'rectangle'}
  squareLogo: Logo = {path: '/static/images/logo/qa4sm_logo_square.webp', height: '80', shape: 'square'}
  logo = signal<Logo>({path: undefined, height: undefined, shape: undefined});

  minWindowWidthFullLogo = 1583;
  maxWindowWidthForSquareLogo = 960;
  noLogoWindowWidth = 660;

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService,
              private settingsService: SettingsService) {

    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        this.isHomePage.set(event.url.includes('/home'))
      }
    });

    this.updateLogo(window.innerWidth);
  }


  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.authStatusChanged(authenticated));
    this.setSettingsValues();
  }

  @HostListener('window:resize', ['$event'])
  onResize(event) {
    this.updateLogo(event.target.innerWidth)
  }

  private updateLogo(windowWidth: number): void {
    this.isLogoDisplayed.set(windowWidth > this.noLogoWindowWidth);
    (windowWidth > this.minWindowWidthFullLogo || windowWidth <= this.maxWindowWidthForSquareLogo)
      ? this.logo.set(this.longLogo) : this.logo.set(this.squareLogo);
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

  logoutObserver = {
    next: (result) => this.onLogoutNext(result),
    error: () => this.toastService.showErrorWithHeader('Something went wrong.',
      'We could not log you out. Please try again or contact our support team.')
  }

  onLogoutNext(result: any): void{
    this.setPreviousUrl('');
    if (result) {// Successful logout
    this.router.navigate(['home'])
      .then(() => this.toastService.showSuccessWithHeader('Logout', 'Successful logout'));
  } else {
      // this part should be removed when the logout subscription is removed from the service
      this.toastService.showErrorWithHeader('Something went wrong.',
        'We could not log you out. Please try again or contact our support team.')
    }
  }

  logout(): void {
    this.authService.logout().subscribe(this.logoutObserver);
  }

  setPreviousUrl(prevUrl: string): void {
    this.authService.setPreviousUrl(prevUrl);
  }

  setSettingsValues(): void {
    const userManualItem = this.items.find(item => item.label === 'Info')
      .items.find(item => item.label === 'User Manual');
    this.settingsService.getAllSettings().subscribe(data => {
      userManualItem.url = data[0].sum_link;
      this.isMaintenancePossible = data[0].potential_maintenance;
      this.potentialMaintenanceDescription = data[0].potential_maintenance_description;
    });
  }

  protected readonly window = window;
}

interface Logo {
  path: string | undefined,
  height: string | undefined,
  shape: 'square' | 'rectangle' | undefined
}
