import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {PlotDto} from '../../modules/core/services/global/plot.dto';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';
import {SettingsDto} from "../../modules/core/services/global/settings.dto";

interface City {
  name: string;
  code: string;
}
const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';

  @Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  imageSource: string;

  carousel_files = [
    //  Files
    homeUrlPrefix + 'map_us_spearman.png',
    homeUrlPrefix + 'smos.jpg',
    homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
    ];
  carousel_links = [
    // Links
    'qa4sm.eu',
    'https://www.esa.int/ESA_Multimedia/Images/2009/09/SMOS',
    'https://www.esa.int/ESA_Multimedia/Images/2016/05/Root-zone_soil_moisture_May_2016',
    ];
  carousel_desc = [
    // Text
    'Image: QA4SM',
    'Image: ESA',
    'Image: ESA',
    ];

  logos = [
    logoUrlPrefix + 'logo_awst.png',
    logoUrlPrefix + 'logo_tuwien_geo.png',
    logoUrlPrefix + 'logo_ffg.png',
  ]

  carousel_images$: Observable<PlotDto[]>;
  settings$: Observable<SettingsDto[]>;
  logos$: Observable<PlotDto[]>;

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              public plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
    this.carousel_images$ = this.getPictures(this.carousel_files);
    this.logos$ = this.getPictures(this.logos);
  }

  getPictures(files: any): Observable<PlotDto[]> {
    let params = new HttpParams();
    files.forEach(file => {
      params = params.append('file', file);
    });
    return this.plotService.getPlots(params);
  }

  getListOfPlots(listOfPlotDto: PlotDto[]): SafeUrl[]{
    return this.plotService.sanitizeManyPlotUrls(listOfPlotDto);
  }

}
