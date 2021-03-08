import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';

@Component({
  selector: 'app-validations',
  templateUrl: './validations.component.html',
  styleUrls: ['./validations.component.scss']
})
export class ValidationsComponent implements OnInit {
  myValidation$: Observable<ValidationrunDto[]>;

  constructor(private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    this.myValidation$ = this.validationrunService.getMyValidationruns();
  }
}
