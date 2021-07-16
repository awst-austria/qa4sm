import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';

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
  logoAwst: string;
  logoEodc: string;
  logoFfg: string;
  logoTuWien: string;

  constructor(private globalParamsService: GlobalParamsService,
              public plotService: WebsiteGraphicsService) { }

  ngOnInit(): void {
    this.logoAwst = logoAwstUrl;
    this.logoEodc = logoEodcUrl;
    this.logoFfg = logoFfgUrl;
    this.logoTuWien = logoTuWienUrl;
  }
  getAppVersion(): string {
    return this.globalParamsService.globalContext.app_version;
   }

}
