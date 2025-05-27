import { Component } from '@angular/core';
import { GlobalParamsService } from '../../modules/core/services/global/global-params.service';

@Component({
  selector: 'qa-terms',
  templateUrl: './terms.component.html',
  styleUrls: ['./terms.component.scss'],
  standalone: false
})
export class TermsComponent {
  public pageUrl = '/terms';
  constructor(private globalParamsService: GlobalParamsService) { }


  getAdminMail(): string {
    return this.globalParamsService.globalContext.admin_mail;
  }
  getSiteURL(): string {
    return this.globalParamsService.globalContext.site_url;
  }
}
