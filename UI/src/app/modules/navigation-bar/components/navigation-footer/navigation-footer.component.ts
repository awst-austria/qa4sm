import {Component} from '@angular/core';
import {Event, NavigationEnd, Router} from '@angular/router';

@Component({
    selector: 'qa-navigation-footer',
    templateUrl: './navigation-footer.component.html',
    styleUrls: ['./navigation-footer.component.scss'],
    standalone: false
})

export class NavigationFooterComponent {

  currentRoute: string = "";
  constructor(private router: Router) {

    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        this.currentRoute = event.url;
      }
    });
  }
}
