import {Component} from '@angular/core';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';
import { Message} from 'primeng/message';
import { RouterLink } from '@angular/router';
import { ScrollTop} from 'primeng/scrolltop';


@Component({
    selector: 'qa-terms',
    standalone: true,
    templateUrl: './terms.component.html',
    styleUrls: ['./terms.component.scss'],
    imports: [Message, ScrollTop, RouterLink],

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
