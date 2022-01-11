import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';

@Component({
  selector: 'qa-validation-page-paginated',
  templateUrl: './validation-page-paginated.component.html',
  styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
  @Input() published: boolean;

  validations: ValidationrunDto[] = [];
  numberOfValidations: number;
  page = 1;
  limit = 10;
  offset = 0;
  order = '-start_time';

  constructor(private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    this.getValidationsAndItsNumber(this.published);
    this.validationrunService.doRefresh.subscribe(value => {
        if (value && value !== 'page'){
          this.updateData(value);
        } else if (value && value === 'page'){
          this.refreshPage();
        }
    });
  }

  getValidationsAndItsNumber(published: boolean): void{
    const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
      .set('order', String(this.order));
    if (!published){
      this.validationrunService.getMyValidationruns(parameters).subscribe(
        response => {
          const {validations, length} = response;
          this.validations = validations;
          this.numberOfValidations = length;
        });
    } else {
      this.validationrunService.getPublishedValidationruns(parameters).subscribe(
        response => {
          const {validations, length} = response;
          this.validations = validations;
          this.numberOfValidations = length;
        });
    }
  }

  handlePageChange(event: number): void {
    this.page = event;
    this.offset = (this.page - 1) * this.limit;
    this.getValidationsAndItsNumber(this.published);
  }

  getOrder(order): void {
    this.order = order;
    this.getValidationsAndItsNumber(this.published);
  }

  updateData(validationId: string): void{
      const indexOfValidation = this.validations.findIndex(validation => validation.id === validationId);
      this.validationrunService.getValidationRunById(validationId).subscribe(data => {
        this.validations[indexOfValidation] = data;
      });
  }

  refreshPage(): void{
    const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
      .set('order', String(this.order));
    this.validationrunService.getMyValidationruns(parameters).subscribe(
      response => {
        const {validations, length} = response;
        this.validations = validations;
        this.numberOfValidations = length;
      });
  }

}
