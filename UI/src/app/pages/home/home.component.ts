import {Component, HostListener, OnInit, Renderer2} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {ActivatedRoute, Router} from '@angular/router';
import {DomSanitizer} from '@angular/platform-browser';
import {ToastService} from 'src/app/modules/core/services/toast/toast.service';

const logoUrlPrefix = '/static/images/logo/';


@Component({
    selector: 'qa-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
    standalone: false
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

  userLoggedIn$ = this.authService.authenticated;

  animationFadeInDownClass = ['fadeindown', 'animation-duration-1000', 'animation-iteration-1']
  animationFadeInClass = ['fadein', 'animation-duration-3000', 'animation-iteration-1']
  animationFadeInLeftClass = ['fadeinleft', 'animation-duration-1000', 'animation-iteration-1']
  animationFadeInRightClass = ['fadeinright', 'animation-duration-1000', 'animation-iteration-1']

  responsiveOptions = [
    { breakpoint: '1024px', numVisible: 1, numScroll: 1 },
    { breakpoint: '768px',  numVisible: 1, numScroll: 1 },
    { breakpoint: '560px',  numVisible: 1, numScroll: 1 }
  ];


  qa4smNewsClass = {
    main: 'NewsContainer fadeInOut',
  }


  applicationTeamClass = {
    partner: 'flex flex-row flex-wrap w-12 gap-1 align-items-center justify-content-center',
    partnerDesc: 'md:w-8 w-12 px-2 text-justify partner-desc gap-1 fadeInLeft',
    partnerLogo: 'md:w-3 w-12 partner-logo align-items-center justify-content-center text-center fadeInRight',
    team: 'flex flex-row flex-wrap gap-2 w-12 align-items-center justify-content-center mb-2',
    teamDesc: 'md:w-9 w-12 text-justify team-desc md:pl-2 pl-2 fadeInRight',
    teamLogo: 'md:w-2 w-12 md:ml-2 ml-2 partner-logo flex align-items-center justify-content-center text-center fadeInLeft'
  }

  settings$ = this.settingsService.getAllSettings();

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              private router: Router,
              private sanitizer: DomSanitizer,
              private renderer: Renderer2,
              private route: ActivatedRoute,
              private toastService: ToastService) {
  }

  ngOnInit() {
    
    // handle opening the login modal window when directed from user email verification
    if (Object.keys(this.route.snapshot.queryParams).length > 0) {
      this.route.queryParams.subscribe(params => {
        if (params['showLogin']) {
          this.authService.switchLoginModal(true, params['message']);
        }
        else if (params['error']) {
          this.toastService.showErrorWithHeader('Verification error', 'Something went wrong with the verification. Please try again or contact our support team.');
        }
      });
    }
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
