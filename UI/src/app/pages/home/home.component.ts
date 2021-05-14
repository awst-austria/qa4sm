import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {GlobalParamsService} from '../../modules/core/services/gloabal-params/global-params.service';

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
    ['assets/landing_page_images/map_us_spearman.png',
      'Image: QA4SM', '#'],
    ['assets/landing_page_images/smos.jpg',
      'Image: ESA', 'https://www.esa.int/spaceinimages/Images/2009/09/SMOS'],
    ['assets/landing_page_images/root-zone_soil_moisture_may_2016.jpg',
      'Image: ESA', 'https://www.esa.int/spaceinimages/Images/2016/05/Root-zone_soil_moisture_May_2016'],
  ];

  processDiagramImage = 'assets/landing_page_images/qa4am_overview_diagram.png';
  datasetSettingsImage = 'assets/landing_page_images/validate.png';
  resultsImage = 'assets/landing_page_images/validation_result_list.png';
  downloadVisualiseImage = 'assets/landing_page_images/validation_result_details.png';

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService,
              private globalParamsService: GlobalParamsService) { }


  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
  }

  getNewsText(): string {
    return this.globalParamsService.globalContext.news;
  }

}
