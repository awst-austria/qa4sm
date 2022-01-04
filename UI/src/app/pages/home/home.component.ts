import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';

interface City {
  name: string,
  code: string
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  landingPageImages = [
    'assets/landing_page_images/map_us_spearman.png',
    'assets/landing_page_images/smos.jpg',
    'assets/landing_page_images/root-zone_soil_moisture_may_2016.jpg',
  ];

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
  }

}
