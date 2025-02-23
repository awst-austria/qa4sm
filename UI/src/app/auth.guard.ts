import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree} from '@angular/router';
import {Observable} from 'rxjs';
import {AuthService} from './modules/core/services/auth/auth.service';
import {map} from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class AuthGuard  {
  constructor(private authService: AuthService, private router: Router) {
  }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const requiresAuth : boolean = route.data['requiresAuth']; // Defines if route requires user to be authenticated or not

    return this.authService.isAuthenticated()
      .pipe(map(auth => {
        if (!auth && requiresAuth) {
          // show login modal if not logged in and try to access a protected route, direct to home page
          this.authService.switchLoginModal(true, 'Please log in to access this page');
          this.router.navigate(['home']);
          return false;
        } else if (auth && !requiresAuth) {
          // If user is logged in and tries to access a page for non-logged in users (signup), direct to home page
          this.router.navigate(['home']);
          return false;
        }
        return true;
    }));
  }
}
