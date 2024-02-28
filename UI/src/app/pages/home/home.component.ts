import {Component, HostListener, OnInit, Renderer2} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {DomSanitizer} from '@angular/platform-browser';

const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';
const videosPrefix = 'static/videos/'


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
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
  },{
    plot: logoUrlPrefix + 'qa4sm_logo_long.webp',
    link: '/home',
    description: 'QA4SM'
  }];


  videos = [
    {
      video: this.sanitizer
        .bypassSecurityTrustResourceUrl('https://www.youtube.com/embed/aFWkxouccRQ?si=gmmbsFsDfo9484TL'),
      title: 'QA4SM - validation set up'
    },
    {
      video: this.sanitizer
        .bypassSecurityTrustResourceUrl('https://www.youtube.com/embed/4pnFyOFfkqk?si=Qimkb5sEBv81t1cM'),
      title: 'QA4SM - validation results'
    },
    {
      video: this.sanitizer
        .bypassSecurityTrustResourceUrl('https://www.youtube.com/embed/rCnUbscpvwY?si=RFdLKN1maRK2IqBv'),
      title: 'QA4SM - upload custom data'
    }
  ];

  settings$: Observable<any>;

  userLoggedIn: boolean;

  animationFadeInDownClass = ['fadeindown', 'animation-duration-1000', 'animation-iteration-1']
  animationFadeInClass = ['fadein', 'animation-duration-3000', 'animation-iteration-1']
  animationFadeInLeftClass = ['fadeinleft', 'animation-duration-1000', 'animation-iteration-1']
  animationFadeInRightClass = ['fadeinright', 'animation-duration-1000', 'animation-iteration-1']

  applicationInfoClass = {
    main: 'flex flex-wrap flex-column row-gap-0 application-info',
    oddRow: 'flex flex-row flex-wrap column-gap-0 w-12 application-row',
    evenRow: 'flex flex-row-reverse flex-wrap column-gap-0 w-12 application-row',
    tile: 'flex flex-column w-6 align-items-center justify-content-start application-tile',
    h1: 'lg:text-6xl md:text-4xl sm:text-2xl text-xl',
    div: 'lg:text-3xl md:text-2xl  sm:text-base text-xs',
  }

  qa4smNewsClass = {
    main: 'app-news flex flex-column flex-wrap justify-content-center align-items-center fadeInOut',
    header: 'line-height-2 lg:text-5xl md:text-4xl sm:text-3xl text-2xl my-1 text-center',
    div: 'line-height-2 lg:text-2xl md:text-xl sm:text-lg text-base py-1'
  }

  opinionSectionClass = {
    main: 'app-news flex flex-column flex-wrap justify-content-center align-items-center mb-2 fadeIn',
    header: 'lg:text-5xl md:text-4xl sm:text-3xl text-2xl mb-2 line-height-2 text-center',
    div: 'line-height-2 lg:text-2xl md:text-xl sm:text-lg text-base py-1 text-center'
  }

  verticalLineClass = {
    main: 'flex flex-column lg:h-6rem h-3rem fadeIn',
  };

  applicationDescriptionClass = 'application-desc flex flex-column flex-wrap h-auto fadeIn';
  applicationIntroClass = {
    main: 'application-intro fadeInOut',
    h1: 'lg:text-6xl md:text-5xl sm:text-4xl text-3xl',
    span: 'lg:text-3xl md:text-2xl'
  }

  videosClass = {
    main: 'application-videos lg:my-5 my-2 w-12 fadeInOut',
    mainDiv: 'flex flex-column align-content-center justify-content-center w-12',
    rowDiv: "w-12 py-2 text-center iframe-container",
    header: "lg:text-3xl md:text-2xl text-base",
  }

  applicationTeamClass = {
    main: 'application-team flex flex-column flex-wrap h-auto lg:my-6 my-4 row-gap-2',
    h1: 'lg:text-6xl md:text-5xl sm:text-4xl text-3xl fadeInOut',
    partner: 'flex flex-row flex-wrap w-12 gap-2 align-items-center justify-content-center',
    partnerDesc: 'md:w-8 w-12 px-3 text-justify partner-desc gap-1 lg:text-xl md:text-base text-xs fadeInLeft',
    partnerLogo: 'md:w-3 w-12 partner-logo align-items-center justify-content-center text-center fadeInRight',
    team: 'flex flex-row flex-wrap gap-2 w-12 align-items-center justify-content-center mb-2',
    teamDesc: 'md:w-9 w-12 text-justify team-desc md:pl-8 pl-2 lg:text-xl md:text-base text-xs fadeInRight',
    teamLogo: 'md:w-2 w-12 md:ml-5 ml-3 partner-logo flex align-items-center justify-content-center text-center fadeInLeft'
  }

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              private router: Router,
              private sanitizer: DomSanitizer,
              private renderer: Renderer2) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.userLoggedIn = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
  }

  goToNews(): void {
    this.router.navigate([], {fragment: "qa4smNews"});
  }


  animations(element): string[] {
    if (element.includes('fadeInOut')) {
      return this.animationFadeInDownClass
    } else if (element.includes('fadeInRight')) {
      return this.animationFadeInRightClass
    } else if (element.includes('fadeInLeft')) {
      return this.animationFadeInLeftClass
    } else if (element.includes('fadeIn')) {
      return this.animationFadeInClass
    }
    return []
  }

  toggleAnimation(element, classes: string[]) {
    classes.forEach(className => {
      this.renderer.addClass(element, className);
    });
  }

  @HostListener('window:scroll', [])
  onScroll() {
    ['.fadeInOut',
      '.fadeIn',
      '.fadeInLeft',
      '.fadeInRight'].forEach(element => {
      this.checkVisibility(element)
    })
  }

  checkVisibility(element) {
    const elements = document.querySelectorAll(element);

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const identifier = entry.target;
          this.toggleAnimation(identifier, this.animations(identifier.className))
        }
      });
    }, {threshold: 0.001}); // Adjust the threshold as needed

    elements.forEach((element) => {
      observer.observe(element);
    });
  }

}
