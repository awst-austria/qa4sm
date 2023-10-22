import {Component, HostListener, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {animate, state, style, transition, trigger} from '@angular/animations';


const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';
const videosPrefix = 'static/videos/'


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  animations: [
    trigger('showNews', [
      state('show', style({ opacity: 1, transform: 'translateY(0)' })),
      state('hide', style({ opacity: 0, transform: 'translateY(20px)' })),
      transition('hide => show', animate('1000ms ease-in')),
    ]),
    trigger('showLine1', [
      state('show', style({ opacity: 1, transform: 'translateY(0)' })),
      state('hide', style({ opacity: 0, transform: 'translateY(20px)' })),
      transition('hide => show', animate('1000ms ease-in')),
    ]),
    trigger('showDesc', [
      state('show', style({ opacity: 1, transform: 'translateY(0)' })),
      state('hide', style({ opacity: 0, transform: 'translateY(20px)' })),
      transition('hide => show', animate('1000ms ease-in')),
    ]),
    trigger('showLine2', [
      state('show', style({ opacity: 1, transform: 'translateY(0)' })),
      state('hide', style({ opacity: 0, transform: 'translateY(20px)' })),
      transition('hide => show', animate('1000ms ease-in')),
    ]),
    trigger('showFeedback', [
      state('show', style({ opacity: 1, transform: 'translateY(0)' })),
      state('hide', style({ opacity: 0, transform: 'translateY(20px)' })),
      transition('hide => show', animate('1000ms ease-in')),
    ]),
  ],
})
export class HomeComponent implements OnInit {
  showNewsState = 'hide';
  showLine1State = 'hide';
  showDescState = 'hide';
  showLine2State = 'hide';
  showFeedbackState = 'hide';

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
    header: 'line-height-2 lg:text-5xl md:text-4xl sm:text-3xl text-2xl my-1 text-center',
    div: 'line-height-2 lg:text-2xl md:text-xl sm:text-lg text-base py-1'
  }

  opinionSectionClass = {
    main: 'app-news flex flex-column flex-wrap justify-content-center align-items-center mb-2',
    header: 'lg:text-5xl md:text-4xl sm:text-3xl text-2xl mb-2 line-height-2 text-center',
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
    header: "lg:text-3xl md:text-2xl text-base",
  }

  applicationTeamClass = {
    main: 'application-team flex flex-column flex-wrap h-auto lg:my-6 my-4 row-gap-2',
    h1: 'lg:text-6xl md:text-5xl sm:text-4xl text-3xl',
    partner: 'flex flex-row flex-wrap w-12 gap-2 align-items-center justify-content-center',
    partnerDesc: 'md:w-8 w-12 px-3 text-justify partner-desc gap-1 lg:text-xl md:text-base text-xs',
    partnerLogo: 'md:w-3 w-12 partner-logo align-items-center justify-content-center text-center',
    team: 'flex flex-row flex-wrap gap-2 w-12 align-items-center justify-content-center mb-2',
    teamDesc: 'md:w-9 w-12 text-justify team-desc md:pl-8 pl-2 lg:text-xl md:text-base text-xs',
    teamLogo: 'md:w-2 w-12 md:ml-5 ml-3 partner-logo flex align-items-center justify-content-center'
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

  // Add a method to change the animation state
  toggleNewsAnimation() {
    this.showNewsState = 'show';
  }
  toggleDescAnimation() {
    this.showDescState = 'show';
  }
  toggleAnimation(element, state){
    switch (element) {
      case '#qa4sm-news':
        this.showNewsState = state;
        break;
      case '#line-1':
        this.showLine1State = state;
        break;
      case '#qa4sm-desc':
        this.showDescState = state;
        break;
      case '#line-2':
        this.showLine2State = state;
        break;
      case '#qa4sm-opinion':
        this.showFeedbackState = state;
        break;
    }
  }
  @HostListener('window:scroll', [])
  onScroll() {
    ['#qa4sm-news', '#line-1' , '#qa4sm-desc', '#line-2', '#qa4sm-opinion'].forEach(element => {
      this.checkVisibility(element)
    })
  }

  checkVisibility(element) {
    const animatedElement = document.querySelector(element);
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.toggleAnimation(element, 'show')
        }
      });
    });

    observer.observe(animatedElement);
  }

}
