import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {WebsiteGraphicsService} from '../../modules/core/services/global/website-graphics.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';
import {HomepageImagesModel} from './homepage-images-model';
import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
import {Gallery} from 'angular-gallery';

const homeUrlPrefix = '/static/images/home/';
const logoUrlPrefix = '/static/images/logo/';

  @Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  carousel_files = [{
    plot: homeUrlPrefix + 'map_us_spearman.png',
    link: '#',
    description: 'Image: QA4SM'}, {
    plot: homeUrlPrefix + 'smos.jpg',
    link: 'https://www.esa.int/ESA_Multimedia/Images/2009/09/SMOS',
    description: 'Image: ESA'}, {
    plot:  homeUrlPrefix + 'root-zone_soil_moisture_may_2016.jpg',
    link: 'https://www.esa.int/ESA_Multimedia/Images/2016/05/Root-zone_soil_moisture_May_2016',
    description: 'Image: ESA'}];

  logo_files = [{
    plot: logoUrlPrefix + 'logo_ffg.png',
    link: 'https://www.ffg.at/',
    description:'FFG'}, {
    plot: logoUrlPrefix + 'logo_tuwien_geo.png',
    link: 'https://www.geo.tuwien.ac.at/',
    description:'GEO'}, {
    plot: logoUrlPrefix + 'logo_awst.png',
    link: 'https://www.awst.at/',
    description:'AWST'}];

  workflow_diagram = [{
    plot: homeUrlPrefix + 'qa4am_overview_diagram.png',
    link: '', description: 'QA4SM workflow'}]

  card_validate = [{
    plot: homeUrlPrefix + 'validate.png',
    link: '', description: 'Validate'}]

  card_validate_result = [{
    plot: homeUrlPrefix + 'validation_result_list.png',
    link: '', description: 'Results'}]

  card_validate_details = [{
    plot: homeUrlPrefix + 'validation_result_details.png',
    link: '', description: 'Download and Visualise'}]

  CarouselImages: HomepageImagesModel[];
  logos: HomepageImagesModel[];
  ImgWorkflowDiagram: HomepageImagesModel[];
  ImgCardValidate: HomepageImagesModel[];
  ImgCardValidateResult: HomepageImagesModel[];
  ImgCardValidateDetails: HomepageImagesModel[];

  settings$: Observable<any>;

  user_logged_in: boolean;

  constructor(private authService: AuthService,
              private settingsService: SettingsService,
              public plotService: WebsiteGraphicsService,
              private gallery: Gallery) {
  }

  ngOnInit(): void {
    this.authService.authenticated.subscribe(authenticated => this.user_logged_in = authenticated);
    this.settings$ = this.settingsService.getAllSettings();
    this.CarouselImages = this.getPictures(this.carousel_files);
    this.logos = this.getPictures(this.logo_files);
    this.ImgWorkflowDiagram = this.getPictures(this.workflow_diagram);
    this.ImgCardValidate = this.getPictures(this.card_validate);
    this.ImgCardValidateResult = this.getPictures(this.card_validate_result);
    this.ImgCardValidateDetails = this.getPictures(this.card_validate_details);
  }

  getPictures(images: any): HomepageImagesModel[]{
    const model = [];
    let plot: any;
    images.forEach(image => {
      const params = new HttpParams().set('file', image.plot);
      plot = this.plotService.getSinglePlot(params);
      model.push(new HomepageImagesModel(plot, image.link, image.description));
    });
    return model;
  }

  getSanitizedPlot(plot: string): SafeUrl{
    return this.plotService.sanitizePlotUrl(plot);
  }

  showGallery(index: number = 0, imagesListObject): void {
      const imagesList = [];
      imagesListObject.forEach(image => {
        imagesList.push({path: this.plotService.plotPrefix + image.plot});
      });
      const prop: any = {};
      prop.component = CarouselComponent;
      prop.images = imagesList;
      prop.index = index;
      prop.arrows = imagesList.length > 1;
      this.gallery.load(prop);
    }
}
