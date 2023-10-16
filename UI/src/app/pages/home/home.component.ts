import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';


const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';
const videosPrefix = 'static/videos/'


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  logoFiles = [{
    plot: logoUrlPrefix + 'logo_awst.png',
    link: 'https://www.awst.at/',
    description: 'AWST'
  }, {
    plot: logoUrlPrefix + 'logo_tuwien_geo.png',
    link: 'https://www.geo.tuwien.ac.at/',
    description: 'GEO'
  }, {
    plot: logoUrlPrefix + 'logo_esa_transparent.png',
    link: 'https://www.esa.int/',
    description: 'ESA'
  }, {
    plot: logoUrlPrefix + 'logo_ffg_transparent.png',
    link: 'https://www.ffg.at/',
    description: 'FFG'
  }, {
      plot: logoUrlPrefix + 'logo_cesbio_transparent.png',
      link: 'https://www.cesbio.cnrs.fr/homepage/',
      description: 'CESBIO'
    },];

  videoValidate = {
    video: videosPrefix + 'QA4SM_Video_Series_I_Validation_4k.mp4',
    title: 'QA4SM - validation set up'
  }

  videoResults = {
    video: videosPrefix + 'QA4SM_Video_Series_II_Results_4K.mp4',
    title: 'QA4SM - validation results'
  }

  videos = [this.videoValidate, this.videoResults];

  settings$: Observable<any>;

  userLoggedIn: boolean;

  applicationInfoClass = 'flex flex-wrap flex-column row-gap-0 application-info';
  applicationInfoOddRowClass = 'flex flex-row flex-wrap column-gap-0 w-12 application-row';
  applicationInfoEvenRowClass = 'flex flex-row-reverse flex-wrap column-gap-0 w-12 application-row';
  applicationInfoTileClass = 'flex flex-column w-6 align-items-center justify-content-start application-tile';

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              private router: Router) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.userLoggedIn = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
  }

  goToNews(): void {
    this.router.navigate([], {fragment: "qa4sm-news"});
  }

}
