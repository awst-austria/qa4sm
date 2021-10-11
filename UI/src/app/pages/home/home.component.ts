import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {Observable} from 'rxjs';

import {Router} from '@angular/router';
import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
import {Gallery} from 'angular-gallery';


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
    link: '#',
    description: 'Image: QA4SM'
  }, {
    plot: homeUrlPrefix + 'smos.jpg',
    link: 'https://www.esa.int/ESA_Multimedia/Images/2009/09/SMOS',
    description: 'Image: ESA'
  }, {
    plot: homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
    link: 'https://www.esa.int/ESA_Multimedia/Images/2016/05/Root-zone_soil_moisture_May_2016',
    description: 'Image: ESA'
  }];

  logoFiles = [{
    plot: logoUrlPrefix + 'logo_ffg.png',
    link: 'https://www.ffg.at/',
    description: 'FFG'
  }, {
    plot: logoUrlPrefix + 'logo_tuwien_geo.png',
    link: 'https://www.geo.tuwien.ac.at/',
    description: 'GEO'
  }, {
    plot: logoUrlPrefix + 'logo_awst.png',
    link: 'https://www.awst.at/',
    description: 'AWST'
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

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              private gallery: Gallery,
              private router: Router) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.userLoggedIn = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
  }

  showGallery(index: number = 0, imagesListObject): void {
    const imagesList = [];
    imagesListObject.forEach(image => {
      imagesList.push({path: image.plot});
    });
    const prop: any = {};
    prop.component = CarouselComponent;
    prop.images = imagesList;
    prop.index = index;
    prop.arrows = imagesList.length > 1;
    this.gallery.load(prop);
  }

  goToSignUp(): void {
    this.router.navigate(['/signup']);
  }
}
