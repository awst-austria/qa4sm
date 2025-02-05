import {Component, OnInit} from '@angular/core';
import {SettingsService} from "../../modules/core/services/global/settings.service";

@Component({
  selector: 'qa-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.scss']
})
export class SignupComponent implements OnInit {
  maintenanceMode = false;

  constructor(private settingsService: SettingsService) { }

  ngOnInit() {
    this.settingsService.getAllSettings().subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
    });
  }
}
