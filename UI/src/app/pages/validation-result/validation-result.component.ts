import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../modules/validation-result/services/dataset-configuration.service';
import {forkJoin} from 'rxjs';
import {ValidationResultModel} from './validation-result-model';

@Component({
  selector: 'app-validation',
  templateUrl: './validation-result.component.html',
  styleUrls: ['./validation-result.component.scss']
})
export class ValidationResultComponent implements OnInit {
  private validationId: string;
  public validationModel: ValidationResultModel;

  constructor(private route: ActivatedRoute,
              private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService) {
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.validationId = params['validationId'];
      let cucc = forkJoin([
        this.validationRunService.getValidationRunById(this.validationId),
        this.datasetConfigurationService.getConfigByValidationrun(this.validationId)
      ]);

      cucc.subscribe(data => console.log(data));

    });
  }

}
