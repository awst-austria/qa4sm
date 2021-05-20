import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParamsModel} from '../../../core/services/validation-run/http-params.model';
import {Observable} from 'rxjs';
import {ValidationSetDto} from '../../services/validation.set.dto';

@Component({
  selector: 'qa-validation-page-paginated',
  templateUrl: './validation-page-paginated.component.html',
  styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
  @Input() published: boolean;

  validations: ValidationrunDto[] = [];
  validationsSet$: Observable<ValidationSetDto>;
  page = 1;
  limit = 10;
  offset = 0;
  order = '-start_time';

  constructor(private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    this.getValidationsAndItsNumber(this.published);
  }

  getValidationsAndItsNumber(published: boolean): void{
    const params = new HttpParamsModel(this.offset, this.limit, this.order);
    if (!published){
    this.validationsSet$ = this.validationrunService.getMyValidationruns(params);
    } else {
      this.validationsSet$ = this.validationrunService.getPublishedValidationruns(params);
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

}
