import {Component, OnInit} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';

const logoUrlPrefix = '/static/images/logo/';
const logoAwstUrl = logoUrlPrefix + 'logo_awst.png';
const logoEodcUrl = logoUrlPrefix + 'logo_eodc.png';
const logoFfgUrl = logoUrlPrefix + 'logo_ffg.png';
const logoTuWienUrl = logoUrlPrefix + 'logo_tuwien_geo.png';
const logoEsa = logoUrlPrefix + 'logo_esa.png';

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
  logoEsa: string;

  constructor(private globalParamsService: GlobalParamsService) { }

  ngOnInit(): void {
    this.logoAwst = logoAwstUrl;
    this.logoEodc = logoEodcUrl;
    this.logoFfg = logoFfgUrl;
    this.logoTuWien = logoTuWienUrl;
    this.logoEsa = logoEsa;
  }
  getAppVersion(): string {
    return this.globalParamsService.globalContext.app_version;
   }

}
