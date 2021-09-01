import {Component, OnInit} from '@angular/core';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {HttpParams} from '@angular/common/http';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {ExtentModel} from '../spatial-extent/extent-model';
import {Observable} from 'rxjs';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../../validation-result/services/dataset-configuration.service';
import {ComparisonService} from '../../services/comparison.service';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
import {Gallery} from 'angular-gallery';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';

@Component({
  selector: 'qa-extent-visualization',
  templateUrl: './extent-visualization.component.html',
  styleUrls: ['./extent-visualization.component.scss']
})

export class ExtentVisualizationComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [], new ExtentModel(true).getIntersection,
  );

  intersectionText: boolean;
  loadingSpinner$: Observable<'open' | 'close'>;
  img: string;

  constructor(private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService,
              private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer,
              private plotService: WebsiteGraphicsService,
              private gallery: Gallery,
              private modalService: ModalWindowService) {
  }

  ngOnInit(): void {
    this.loadingSpinner$ = this.modalService.watch();
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.comparisonModel = comparison;
        this.getExtentImage(comparison);
        this.intersectionText = this.comparisonModel.getIntersection;
      }
    });
  }

  getExtentImage(comparisonModel: Validations2CompareModel): void {
    // Get all the plots for a specific comparison and metric
    let parameters = new HttpParams()
      .set('get_intersection', String(comparisonModel.getIntersection));

    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    this.comparisonService.getComparisonExtentImage(parameters).subscribe(data => {
      this.img = data;
    });
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  showImage(image): void {
    const sanitizedImage = this.sanitizePlotUrl(image);
    const imagesList = [{path: sanitizedImage}];
    const prop: any = {};
    prop.component = CarouselComponent;
    prop.images = imagesList;
    prop.index = 0;
    prop.arrows = imagesList.length > 1;
    this.gallery.load(prop);
  }

}
