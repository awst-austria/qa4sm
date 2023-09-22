import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {Observable} from 'rxjs';


const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public carouselFiles = [{
    plot: homeUrlPrefix + 'map_us_spearman.jpg',
    attrLink: '#',
    description: 'Image: QA4SM'
  }, {
    plot: homeUrlPrefix + 'smos_full.jpg',
    attrLink: 'https://www.esa.int/ESA_Multimedia/Images/2009/09/SMOS',
    description: 'Image: ESA'
  }, {
    plot: homeUrlPrefix + 'Root-zone_soil_moisture_May_2016.jpg',
    attrLink: 'https://www.esa.int/ESA_Multimedia/Images/2016/05/Root-zone_soil_moisture_May_2016',
    description: 'Image: ESA'
  }];

  logoFiles = [{
    plot: logoUrlPrefix + 'logo_awst.png',
    link: 'https://www.awst.at/',
    description: 'AWST'
  }, {
    plot: logoUrlPrefix + 'logo_tuwien_geo.png',
    link: 'https://www.geo.tuwien.ac.at/',
    description: 'GEO'
  }, {
    plot: logoUrlPrefix + 'logo_esa.png',
    link: 'https://www.esa.int/',
    description: 'ESA'
  }, {
    plot: logoUrlPrefix + 'logo_ffg.png',
    link: 'https://www.ffg.at/',
    description: 'FFG'
  }];

  workflowDiagram = [{
    plot: homeUrlPrefix + 'qa4am_overview_diagram.png',
    link: '', description: 'QA4SM workflow'
  }];

  cardValidate = [{
    plot: homeUrlPrefix + 'validate.png',
    link: '', description: 'Validate'
  }];

  cardValidateResult = [{
    plot: homeUrlPrefix + 'validation_result_list.png',
    link: '', description: 'Results'
  }];

  cardValidateDetails = [{
    plot: homeUrlPrefix + 'validation_result_details.png',
    link: '', description: 'Download and Visualise'
  }];

  settings$: Observable<any>;

  userLoggedIn: boolean;

  applicationInfoClass = 'flex flex-wrap flex-column row-gap-0 application-info';
  applicationInfoOddRowClass = 'flex flex-row flex-wrap column-gap-0 w-12';
  applicationInfoEvenRowClass = 'flex flex-row-reverse flex-wrap column-gap-0 w-12';
  applicationInfoTileClass = 'flex flex-column w-6 align-items-center justify-content-center application-tile';

  constructor(private authService: AuthService,
              private settingsService: SettingsService) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.userLoggedIn = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
    this.settings$.subscribe(data => {
    }
    );
  }

}
