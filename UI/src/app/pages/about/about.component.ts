import { Component, OnInit } from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/gloabal-params/global-params.service';

@Component({
  selector: 'qa-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent implements OnInit {

  constructor(private globalParamsService: GlobalParamsService) { }

  ngOnInit(): void {
  }
  getAppVersion(): string {
    return this.globalParamsService.globalContext.app_version;
   }

}
