import {ChangeDetectionStrategy, Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../modules/validation-result/services/dataset-configuration.service';
import {ValidationResultModel} from './validation-result-model';
import {ModalWindowService} from '../../modules/core/services/global/modal-window.service';

@Component({
  selector: 'app-validation',
  templateUrl: './validation-result.component.html',
  styleUrls: ['./validation-result.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidationResultComponent implements OnInit {
  public validationId: string;
  public validationModel: ValidationResultModel;
  public isPublishingWindowOpen: boolean;

  constructor(private route: ActivatedRoute,
              private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService,
              private modalWindowService: ModalWindowService) {
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.validationId = params.validationId;
      this.validationModel = new ValidationResultModel(
        this.validationRunService.getValidationRunById(this.validationId),
        this.datasetConfigurationService.getConfigByValidationrun(this.validationId)
      );
    });
    this.modalWindowService.watch().subscribe(state => {
      this.isPublishingWindowOpen = state === 'open';
    });
  }

  update(): void{
    this.validationModel.validationRun = this.validationRunService.getValidationRunById(this.validationId);
  }

}
