import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {PlotDto} from '../../modules/core/services/global/plot.dto';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';

const logoUrlPrefix = '/static/images/logo/';
const logoAwstUrl = logoUrlPrefix + 'logo_awst.png';
const logoEodcUrl = logoUrlPrefix + 'logo_eodc.png';
const logoFfgUrl = logoUrlPrefix + 'logo_ffg.png';
const logoTuWienUrl = logoUrlPrefix + 'logo_tuwien_geo.png';

@Component({
  selector: 'qa-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})

export class AboutComponent implements OnInit {
  logoAwst$: Observable<PlotDto[]>;
  logoEodc$: Observable<PlotDto[]>;
  logoFfg$: Observable<PlotDto[]>;
  logoTuWien$: Observable<PlotDto[]>;

  constructor(private globalParamsService: GlobalParamsService,
              public plotService: WebsiteGraphicsService) { }

  ngOnInit(): void {
    this.logoAwst$ = this.getLogos([logoAwstUrl]);
    this.logoEodc$ = this.getLogos([logoEodcUrl]);
    this.logoFfg$ = this.getLogos([logoFfgUrl]);
    this.logoTuWien$ = this.getLogos([logoTuWienUrl]);
  }
  getAppVersion(): string {
    return this.globalParamsService.globalContext.app_version;
   }

  getLogos(files: any): Observable<PlotDto[]> {
    let params = new HttpParams();
    files.forEach(file => {
      params = params.append('file', file);
    });
    return this.plotService.getPlots(params);
  }
  sanitizePlotUrl(plotUrl: string): SafeUrl{
    return this.plotService.sanitizePlotUrl(plotUrl);
  }

}
