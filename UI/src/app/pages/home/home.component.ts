import {Component, OnInit} from '@angular/core';
import {Carousel} from 'primeng/carousel';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  landingPageImages = [
    'assets/landing_page_images/map_us_spearman.png',
    'assets/landing_page_images/root-zone_soil_moisture_may_2016.jpg',
    'assets/landing_page_images/smos.jpg'
  ];

  constructor() {
  }

  ngOnInit(): void {
  }

}
