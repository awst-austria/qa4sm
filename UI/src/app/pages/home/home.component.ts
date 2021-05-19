import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
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
    homeUrlPrefix + 'map_us_spearman.png',
    homeUrlPrefix + 'smos.jpg',
    homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
  ];
  images$: Observable<PlotDto[]>;

  loginButtonDisabled: boolean = false;

  constructor(private authService: AuthService,
              public plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this. images$ = this.getPictures(this.landingPageImages);
    this.authService.authenticated.subscribe(authenticated => this.loginButtonDisabled = authenticated);
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
