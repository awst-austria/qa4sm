import {Component, HostListener, Input, OnInit} from '@angular/core';
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

  commonClasses = 'col-12 md:col-10 lg:col-10 xl:col-8  xl:col-offset-2 '
  myValClasses = this.commonClasses + 'col-offset-4  md:col-offset-3  lg:col-offset-2'
  publishedValClasses = this.commonClasses +  'md:col-offset-1 lg:col-offset-1'

  validations: ValidationrunDto[] = [];
  numberOfValidations: number;
  page = 1;
  limit = 10;
  offset = 0;
  order = '-start_time';
  selectionActive$ = new BehaviorSubject(false);
  selectedValidations$: BehaviorSubject<any> = new BehaviorSubject<any>([]);


  isLoading: boolean = false;
  endOfPage: boolean = false;
  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.getValidationsAndItsNumber(this.published);
    this.validationrunService.doRefresh.subscribe(value => {
      if (value && value !== 'page') {
        this.updateData(value);
      } else if (value && value === 'page') {
        this.refreshPage();
      }
    });
  }

  @HostListener('window:scroll', ['$event'])
  onScroll() {
    const windowHeight = 'innerHeight' in window ? window.innerHeight : document.documentElement.offsetHeight;
    const body = document.body, html = document.documentElement;
    const docHeight = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    const windowBottom = windowHeight + window.pageYOffset;

    if (windowBottom >= docHeight - 1 && !this.isLoading && !this.endOfPage) {
      this.page++;
      this.getValidationsAndItsNumber(this.published);
    }
  }

  getValidationsAndItsNumber(published: boolean): void {
    // if (this.isLoading || this.endOfPage) {
    //   return;
    // }
    const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
      .set('order', String(this.order));
    if (!published) {
      this.validationrunService.getMyValidationruns(parameters).subscribe(
        response => {
          const {validations, length} = response;
          this.numberOfValidations = length;
          const maxPages = length / this.limit;
          if (validations.length){
            this.validations = this.validations.concat(validations);
            this.page++;

            if (this.page >= maxPages){
              this.endOfPage = true;
            }
          } else {
            this.endOfPage = true;
          }

          this.isLoading = false;
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

  updateData(validationId: string): void {
    const indexOfValidation = this.validations.findIndex(validation => validation.id === validationId);
    this.validationrunService.getValidationRunById(validationId).subscribe(data => {
      this.validations[indexOfValidation] = data;
    });
  }

  refreshPage(): void {
    const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
      .set('order', String(this.order));
    this.validationrunService.getMyValidationruns(parameters).subscribe(
      response => {
        const {validations, length} = response;
        this.validations = validations;
        this.numberOfValidations = length;
      });
  }

  handleMultipleSelection(event): void {
    this.selectionActive$.next(event.activate)
    this.selectedValidations$.next(event.selected.value)
  }

  updateSelectedValidations(checked: boolean, id: number): void {
    let selectedValidations = this.selectedValidations$.getValue();
    if (checked) {
      selectedValidations = [...selectedValidations, id];
    } else {
      selectedValidations = selectedValidations.filter(selectedId => selectedId !== id);
    }
    this.selectedValidations$.next(selectedValidations)
  }

}
