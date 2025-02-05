import {Component} from '@angular/core';
import {SettingsService} from "../../modules/core/services/global/settings.service";

@Component({
  selector: 'qa-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.scss']
})
export class SignupComponent{

  constructor(private settingsService: SettingsService) { }
}
