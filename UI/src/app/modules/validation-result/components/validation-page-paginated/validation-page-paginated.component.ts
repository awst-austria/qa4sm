import {Component, HostListener, Input, OnInit, signal} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {BehaviorSubject, EMPTY, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';

@Component({
  selector: 'qa-validation-page-paginated',
  templateUrl: './validation-page-paginated.component.html',
  styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
  @Input() published: boolean;
  validations: ValidationrunDto[] = [];
  maxNumberOfPages: number;
  currentPage = 1;
  limit = 10;
  offset = 0;
  order = '-start_time';
  selectionActive$ = new BehaviorSubject(false);
  allSelected$ = new BehaviorSubject(false);
  action$ = new BehaviorSubject(null);
  selectedValidations$: BehaviorSubject<any> = new BehaviorSubject<any>([]);


  isLoading: boolean = false;
  orderChange: boolean = false;
  endOfPage: boolean = false;

  dataFetchError = signal(false);

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.getValidationsAndItsNumber(this.published);
    this.validationrunService.doRefresh$.subscribe(value => {
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
    const docHeight = document.documentElement.scrollHeight;
    const windowBottom = windowHeight + window.scrollY;

    if (windowBottom >= docHeight - 1 && !this.isLoading && !this.endOfPage) {
      this.currentPage++;
      this.offset = (this.currentPage - 1) * this.limit;
      this.getValidationsAndItsNumber(this.published);
    }
  }

  getValidationsAndItsNumber(published: boolean): void {
    this.isLoading = true;
    const parameters = new HttpParams().set('offset', String(this.offset)).set('limit', String(this.limit))
      .set('order', String(this.order));
    if (!published) {
      this.validationrunService.getMyValidationruns(parameters)
        .pipe(
          catchError(() => this.onDataFetchError())
        )
        .subscribe(
          response => {
            this.handleFetchedValidations(response);
          });
    } else {
      this.validationrunService.getPublishedValidationruns(parameters)
        .pipe(
          catchError(() => this.onDataFetchError())
        )
        .subscribe(
          response => {
            this.handleFetchedValidations(response);
          });
    }
  }

  handleFetchedValidations(serverResponse: { validations: ValidationrunDto[]; length: number; }): void {
    const {validations, length} = serverResponse;
    if (!this.maxNumberOfPages) {
      this.maxNumberOfPages = Math.ceil(length / this.limit);
    }

    if (this.orderChange) {
      this.validations = validations;
    } else {
      if (validations.length) {
        this.validations = this.validations.concat(validations);

        if (this.allSelected$.value) {
          const selectedValidations = [];
          const select_archived = this.action$.value === 'unarchive';
          this.validations.forEach(val => {
            if (val.is_archived === select_archived && val.is_unpublished) {
              selectedValidations.push(val.id);
            }
          })
          this.selectedValidations$.next(selectedValidations);
        }

        if (this.currentPage > this.maxNumberOfPages) {
          this.setEndOfPage();
        }
      } else {
        this.setEndOfPage();
      }
    }
    this.orderChange = false;
    this.isLoading = false;
  }

  getOrder(order): void {
    this.order = order;
    this.orderChange = true;
    this.getValidationsAndItsNumber(this.published);
  }

  setEndOfPage() {
    this.endOfPage = true;
    this.limit = this.validations.length;
    this.offset = 0;
  }


  updateData(validationId: string): void {
    const indexOfValidation = this.validations
      .findIndex(validation => validation.id === validationId);
    this.validationrunService.getValidationRunById(validationId)
      .pipe(
        catchError(() => EMPTY)
      )
      .subscribe(data => {
        this.validations[indexOfValidation] = data;
      });
  }

  refreshPage(): void {
    const parameters = new HttpParams()
      .set('offset', String(this.offset))
      .set('limit', String(this.limit))
      .set('order', String(this.order));
    this.validationrunService.getMyValidationruns(parameters)
      .pipe(
        catchError(() => this.onDataFetchError())
      )
      .subscribe(
        response => {
          const {validations, length} = response;
          this.validations = validations;
        });
  }

  handleMultipleSelection(event): void {
    this.selectionActive$.next(event.active);
    this.action$.next(event.action);
    this.selectedValidations$.next(event.selected.value);
    this.allSelected$.next(event.allSelected);
  }

  updateSelectedValidations(checked: string[], id: string): void {
    let selectedValidations = this.selectedValidations$.getValue();
    if (checked.includes(id)) {
      selectedValidations = [...selectedValidations, id];
    } else {
      selectedValidations = selectedValidations.filter((selectedId: string) => selectedId !== id);
    }
    this.selectedValidations$.next(selectedValidations);
  }

  checkIfEnabled(valrun: ValidationrunDto): boolean {
    let condition = valrun.is_unpublished && !valrun.is_archived;

    if (this.action$.value === 'unarchive') {
      condition = valrun.is_unpublished  && valrun.is_archived;
    }

    return condition;
  }

  onDataFetchError(): Observable<never> {
    this.dataFetchError.set(true);
    return EMPTY;
  }

}
