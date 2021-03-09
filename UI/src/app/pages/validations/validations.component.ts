import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';

@Component({
  selector: 'app-validations',
  templateUrl: './validations.component.html',
  styleUrls: ['./validations.component.scss']
})
export class ValidationsComponent implements OnInit {
  myValidation$: Observable<ValidationrunDto[]>;

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.myValidation$ = this.validationrunService.getMyValidationruns();
  }
}
