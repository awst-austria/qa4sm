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
    plot: logoUrlPrefix + 'logo_awst.webp',
    link: 'https://www.awst.at/',
    description: 'AWST'
  }, {
    plot: logoUrlPrefix + 'logo_tuwien_geo.webp',
    link: 'https://www.geo.tuwien.ac.at/',
    description: 'GEO'
  }, {
    plot: logoUrlPrefix + 'logo_esa_transparent.webp',
    link: 'https://www.esa.int/',
    description: 'ESA'
  }, {
    plot: logoUrlPrefix + 'logo_ffg_transparent.webp',
    link: 'https://www.ffg.at/',
    description: 'FFG'
  }, {
    plot: logoUrlPrefix + 'logo_cesbio_transparent.webp',
    link: 'https://www.cesbio.cnrs.fr/homepage/',
    description: 'CESBIO'
  },];


  videos = [
    {
      video: videosPrefix + 'QA4SM_Video_Series_I_Validation_4k.mp4',
      title: 'QA4SM - validation set up'
    },
    {
      video: videosPrefix + 'QA4SM_Video_Series_II_Results_4K.mp4',
      title: 'QA4SM - validation results'
    }
  ];

  settings$: Observable<any>;

  userLoggedIn: boolean;

  applicationInfoClass = {
    main: 'flex flex-wrap flex-column row-gap-0 application-info',
    oddRow: 'flex flex-row flex-wrap column-gap-0 w-12 application-row',
    evenRow: 'flex flex-row-reverse flex-wrap column-gap-0 w-12 application-row',
    tile: 'flex flex-column w-6 align-items-center justify-content-start application-tile',
    h1: 'lg:text-6xl md:text-4xl sm:text-2xl text-xl',
    div: 'lg:text-3xl md:text-2xl  sm:text-base text-xs',
  }

  newsSectionClass = {
    main: 'app-news flex flex-column flex-wrap justify-content-center align-items-center',
    h3: 'line-height-2 lg:text-5xl md:text-4xl sm:text-3xl text-2xl my-1 text-center',
    div: 'line-height-2 lg:text-2xl md:text-xl sm:text-lg text-base py-1'
  }

  opinionSectionClass = {
    main: 'app-news flex flex-column flex-wrap justify-content-center align-items-center mb-2',
    h3: 'lg:text-5xl md:text-4xl sm:text-3xl text-2xl mb-2 line-height-2 text-center',
    div: 'line-height-2 lg:text-2xl md:text-xl sm:text-lg text-base py-1 text-center'
  }

  verticalLineClass = {
    main: 'flex flex-column lg:h-6rem h-3rem',
  };

  applicationDescriptionClass = 'application-desc flex flex-column flex-wrap h-auto';
  applicationIntroClass = {
    main: 'application-intro',
    h1: 'lg:text-6xl md:text-5xl sm:text-4xl text-3xl',
    span: 'lg:text-3xl md:text-2xl'
  }

  videosClass = {
    main: 'application-videos lg:my-5 my-2 w-12',
    mainDiv: 'flex flex-column align-content-center justify-content-center',
    rowDiv: "w-12 py-2 text-center",
    h4: "lg:text-3xl md:text-2xl text-base",
  }

  applicationTeamClass = {
    main: 'application-team flex flex-column flex-wrap h-auto lg:my-6 my-4 row-gap-2',
    h1: 'lg:text-6xl md:text-5xl sm:text-4xl text-3xl',
    partner: 'flex flex-row flex-wrap w-12 align-items-center justify-content-center',
    partnerDesc: 'w-8 pl-3 text-justify partner-desc gap-1 lg:text-xl md:text-base text-xs',
    partnerLogo: 'w-3 partner-logo flex flex-wrap align-items-center justify-content-center',
    team: 'flex flex-row flex-wrap gap-1 w-12 align-items-center justify-content-center mb-2',
    teamDesc: 'w-9 pl-3 text-justify team-desc px-5 lg:text-xl md:text-base text-xs',
    teamLogo: 'w-2 partner-logo flex align-items-center justify-content-center'
  }

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
