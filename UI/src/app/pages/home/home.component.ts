import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {PlotDto} from '../../modules/core/services/global/plot.dto';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';

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

  landingPageImages = [
    [homeUrlPrefix + 'map_us_spearman.png',
      'Image: QA4SM', '#'],
    [homeUrlPrefix + 'smos.jpg',
      'Image: ESA', 'https://www.esa.int/spaceinimages/Images/2009/09/SMOS'],
    [homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
      'Image: ESA', 'https://www.esa.int/spaceinimages/Images/2016/05/Root-zone_soil_moisture_May_2016'],
  ];
  images$: Observable<PlotDto[]>;

  processDiagramImage = 'assets/landing_page_images/qa4am_overview_diagram.png';
  datasetSettingsImage = 'assets/landing_page_images/validate.png';
  resultsImage = 'assets/landing_page_images/validation_result_list.png';
  downloadVisualiseImage = 'assets/landing_page_images/validation_result_details.png';

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService,
              private globalParamsService: GlobalParamsService,
              public plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this.images$ = this.getPictures(this.landingPageImages);
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
  }

  getNewsText(): string {
    return this.globalParamsService.globalContext.news;
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
