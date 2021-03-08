import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';

@Component({
  selector: 'qa-published-validations',
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss']
})
export class PublishedValidationsComponent implements OnInit {
  publishedValidation$: Observable<ValidationrunDto[]>;

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.publishedValidation$ = this.validationrunService.getPublishedValidationruns();
  }
}
