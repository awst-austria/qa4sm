import {ChangeDetectionStrategy, Component, OnInit, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../modules/validation-result/services/dataset-configuration.service';
import {ValidationResultModel} from './validation-result-model';
import {catchError} from 'rxjs/operators';
import {EMPTY} from 'rxjs';

@Component({
  selector: 'qa-validation',
  templateUrl: './validation-result.component.html',
  styleUrls: ['./validation-result.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidationResultComponent implements OnInit {
  public validationId: string;
  public validationModel: ValidationResultModel;
  dataFetchError = signal(false);

  constructor(private route: ActivatedRoute,
              private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService) {
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.validationId = params.validationId;
      this.validationModel = new ValidationResultModel(
        this.validationRunService.getValidationRunById(this.validationId)
          .pipe(
            catchError(() => {
              this.dataFetchError.set(true);
              return EMPTY;
            })
          ),
        this.datasetConfigurationService.getConfigByValidationrun(this.validationId)
          .pipe(
            catchError(() => {
              this.dataFetchError.set(true);
              return EMPTY;
            })
          )
      );
    });
  }

  update(): void{
    this.validationModel.validationRun$ = this.validationRunService.getValidationRunById(this.validationId)
      .pipe(
      catchError(() => {
        this.dataFetchError.set(true);
          return EMPTY;
      })
    );
  }

}
