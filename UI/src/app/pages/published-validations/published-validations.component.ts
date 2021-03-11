import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {ValidationSetDto} from '../../modules/validation-result/services/validation.set.dto';
import {HttpParams} from '@angular/common/http';

@Component({
  selector: 'qa-published-validations',
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss']
})
export class PublishedValidationsComponent implements OnInit {
  publishedValidation$: Observable<ValidationSetDto>;
  validations: ValidationrunDto[] = [];
  numberOfValidations: number;
  page = 1;
  limit = 10;
  offset = 0;
  parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit));

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.getValidationsAndItsNumber();
  }

  getValidationsAndItsNumber(): void{
    console.log(this.offset, this.limit);
    let parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit));
    this.validationrunService.getPublishedValidationruns(parameters).subscribe(
      response => {
        const {validations, length} = response;
        this.validations = validations;
        this.numberOfValidations = length;
      });
  }

  handlePageChange(event: number): void {
    this.page = event;
    this.offset = (this.page - 1) * this.limit;
    this.getValidationsAndItsNumber();
  }

}
