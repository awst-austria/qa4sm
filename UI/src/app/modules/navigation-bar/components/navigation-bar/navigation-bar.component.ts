import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../../core/services/auth/auth.service';
import {faCoffee} from '@fortawesome/free-solid-svg-icons/faCoffee';
import {
  faBalanceScale, faBook,
  faCog,
  faDatabase,
  faDoorOpen,
  faInfoCircle,
  faQuestionCircle,
  faUserCircle,
  faUserCog
} from '@fortawesome/free-solid-svg-icons';
import {ToastService} from '../../../toast/services/toast.service';
import {Router} from '@angular/router';

@Component({
  selector: 'navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {

  logoutButtonDisabled = true;
  userProfileButtonDisabled = true;
  isCollapsed = true;
  aboutIcon = faInfoCircle;
  helpIcon = faQuestionCircle;
  datasetsIcon = faDatabase;
  termsIcon = faBalanceScale;
  profileIcon = faUserCog;
  logoutIcon = faDoorOpen;
  validateIcon = faCog;
  myValidationsIcon = faUserCircle;
  publishedValidationsIcon = faBook;


  constructor(private authService: AuthService, private toastService: ToastService, private router: Router) {

  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.authStatusChanged(authenticated));
  }

  private authStatusChanged(authenticated: boolean) {
    this.logoutButtonDisabled = !authenticated;
    this.userProfileButtonDisabled = !authenticated;
  }

  logout() {
    this.authService.logout().subscribe(result => {
        if (result) {//Successful logout
          this.router.navigate(['home']).then(value => this.toastService.showSuccessWithHeader('Logout','Successful logout'))
        }
      }
    );
  }

}
