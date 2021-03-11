import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';
import {ValidationSetDto} from '../../modules/validation-result/services/validation.set.dto';
import {HttpParams} from '@angular/common/http';

@Component({
  selector: 'app-validations',
  templateUrl: './validations.component.html',
  styleUrls: ['./validations.component.scss']
})
export class ValidationsComponent implements OnInit {
  myValidation$: Observable<ValidationSetDto>;
  validations: ValidationrunDto[] = [];
  numberOfValidations: number;
  page = 1;
  limit = 10;
  offset = 0;
  parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit));

  constructor(private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    this.getValidationsAndItsNumber();
  }

  getValidationsAndItsNumber(): void{
    console.log(this.offset, this.limit);
    let parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit));
    this.validationrunService.getMyValidationruns(parameters).subscribe(
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
