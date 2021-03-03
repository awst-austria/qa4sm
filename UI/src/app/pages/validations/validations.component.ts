import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {DatasetDto} from '../../modules/dataset/services/dataset.dto';
import {DatasetVersionDto} from '../../modules/dataset/services/dataset-version.dto';
import {DatasetVariableDto} from '../../modules/dataset/services/dataset-variable.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';

@Component({
  selector: 'app-validations',
  templateUrl: './validations.component.html',
  styleUrls: ['./validations.component.scss']
})
export class ValidationsComponent implements OnInit {
  myValidation$: Observable<ValidationrunDto[]>;
  datasets?: DatasetDto[] = [];
  versions?: DatasetVersionDto[] = [];
  variables?: DatasetVariableDto[] = [];

  constructor(private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    this.myValidation$ = this.validationrunService.getMyValidationruns();
    // this.getDatasetsInfo();
  }

  getDatasetsInfo(){
    this.validationrunService.getAllDatasets(this.datasets);
    this.validationrunService.getAllVersions(this.versions);
    this.validationrunService.getAllVariables(this.variables);
  }
}
