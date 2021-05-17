import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';
import {HomepageImagesModel} from './homepage-images-model';

interface City {
  name: string;
  code: string;
}

const homeUrlPrefix = '/static/images/home/';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  images = [
    {plot: homeUrlPrefix + 'map_us_spearman.png',
    link: 'qa4sm.eu',
    description: 'Image: QA4SM'},
    {plot: homeUrlPrefix + 'smos.jpg',
      link: 'https://www.esa.int/ESA_Multimedia/Images/2009/09/SMOS',
      description: 'Image: ESA'},
    {plot:  homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
      link: 'https://www.esa.int/ESA_Multimedia/Images/2016/05/Root-zone_soil_moisture_May_2016',
      description: 'Image: ESA'}
  ];

  imagesModel: HomepageImagesModel[];
  settings$: Observable<any>;

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              public plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    console.log(this.images);
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
    this.imagesModel = this.getPictures(this.images);
  }

  getPictures(images: any): HomepageImagesModel[]{
    const model = [];
    let plot: any;
    images.forEach(image => {
      const params = new HttpParams().set('file', image.plot);
      plot = this.plotService.getSinglePlot(params);
      model.push(new HomepageImagesModel(plot, image.link, image.description));
    });
    return model;
  }

  getSanitizedPlot(plot: string): SafeUrl{
    return this.plotService.sanitizePlotUrl(plot);
  }

}
