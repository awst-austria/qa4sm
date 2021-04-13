import { Component, OnInit } from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/gloabal-params/global-params.service';

@Component({
  selector: 'qa-terms',
  templateUrl: './terms.component.html',
  styleUrls: ['./terms.component.scss']
})
export class TermsComponent implements OnInit {

  constructor(private globalParamsService: GlobalParamsService) { }

  ngOnInit(): void {
  }
  getAdminMail(): string {
    return this.globalParamsService.globalContext.admin_mail;
  }
  getSiteURL(): string {
    return this.globalParamsService.globalContext.site_url;
  }
}
