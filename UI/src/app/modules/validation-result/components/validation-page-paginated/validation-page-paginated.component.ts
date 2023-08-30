import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {BehaviorSubject} from 'rxjs';

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
  selectionActive$ = new BehaviorSubject(false);
  allSelected$ = new BehaviorSubject(false);
  selectedValidations$: BehaviorSubject<any> = new BehaviorSubject<any>([]);

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

  handleMultipleSelection(event): void{
      if (!this.selectionActive$.value){
        this.selectionActive$.next(event.activate)
      }

      if (event.selectAll){
        this.selectAllModifiableValidations()
      } else {
        this.cleanSelection()
      }
  }

    closeAndCleanSelection(): void{
        this.selectionActive$.next(false)
        this.cleanSelection()
    }

    selectAllModifiableValidations(): void{
      const selectedValidations = [];
      this.validations.forEach(val => {
        if (!val.is_archived && val.is_unpublished){
          selectedValidations.push(val.id)
        }
        this.selectedValidations$.next(selectedValidations);
      })
    }

  updateSelectedValidations(checked: boolean, id: number): void{
    let selectedValidations = this.selectedValidations$.getValue();
      if (checked) {
        selectedValidations = [...selectedValidations, id];
      } else {
        selectedValidations = selectedValidations.filter(selectedId => selectedId !== id);
      }
      this.selectedValidations$.next(selectedValidations)
    }

    cleanSelection(): void {
      this.selectedValidations$.next([])
    }

    deleteMultipleValidations(): void{
      console.log('Monika')
    }

}
