import { Component, OnInit } from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/gloabal-params/global-params.service';

@Component({
  selector: 'qa-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.scss']
})
export class HelpComponent implements OnInit {

  constructor(private globalParamsService: GlobalParamsService) { }

  ngOnInit(): void {
  }
  getAdminMail(): string {
    return this.globalParamsService.globalContext.admin_mail;
   }
  getExpiryPeriod(): string {
    return this.globalParamsService.globalContext.expiry_period;
   }
  getWarningPeriod(): string {
    return this.globalParamsService.globalContext.warning_period;
   }

}
