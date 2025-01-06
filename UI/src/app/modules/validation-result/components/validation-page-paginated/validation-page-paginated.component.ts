import {Component, HostListener, Input, OnInit, signal} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {BehaviorSubject, combineLatest, EMPTY, forkJoin, Observable} from 'rxjs';
import {catchError, map} from 'rxjs/operators';
import {FilterPayload, FilterConfig} from 'src/app/modules/validation-result/components/filtering-form/filterPayload.interface';

import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';

///// MOVE THIS WHEN FINISHED TESTING ///////
import { FilteringFormComponent } from 'src/app/modules/validation-result/components/filtering-form/filtering-form.component';

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


  filterPayload: FilterPayload; //= {  statuses: [], name: null, spatialRef: [], temporalRef: [], scalingRef: [] };

  dataFetchError = signal(false);


  constructor(private validationrunService: ValidationrunService, private datasetConfigService: DatasetConfigurationService, private datasetService: DatasetService) {
    //initialise empty filterPayload with empty array or null for filters with/without isArray
    this.filterPayload = Object.entries(FilteringFormComponent.FILTER_CONFIGS).reduce((acc, [_, config]) => {
      acc[config.backendField] = config.isArray ? [] : null;
      return acc;
    }, {} as FilterPayload);
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

    const scrollThreshold = 0.9; //Load further results at 90% scroll - more robust
    if ((windowBottom / docHeight) >= scrollThreshold && !this.isLoading && !this.endOfPage) {
      this.currentPage++;
      this.offset = (this.currentPage - 1) * this.limit;
      this.getValidationsAndItsNumber(this.published);
    }
  }

  getValidationsAndItsNumber(published: boolean): void {
    this.isLoading = true;

    let parameters = new HttpParams()
      .set('offset', String(this.offset))
      .set('limit', String(this.limit))
      .set('order', String(this.order));

    // Add filters from payload to query parameters
    Object.entries(FilteringFormComponent.FILTER_CONFIGS).forEach(([key, config]) => {
      const values = this.filterPayload[config.backendField];
      if (values) {
        if (config.isArray && Array.isArray(values) && values.length > 0) {
          values.forEach(value => {
            parameters = parameters.append(config.backendField, value);
          });
        } else if (!config.isArray && values) {
          const paramValue = Array.isArray(values) ? values[0] : values;
          parameters = parameters.set(config.backendField, String(paramValue));
        }
      }
    });
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
    
    this.maxNumberOfPages = Math.ceil(length / this.limit);
  
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

        if (this.validations.length < length) {
          this.currentPage = Math.floor(this.validations.length / this.limit);
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

  getFilter(filter: FilterPayload): void {
    this.filterPayload = filter;
    this.orderChange =true;

    // Reset page
    this.currentPage = 1;
    this.offset = 0;
    this.endOfPage = false;
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
    let condition = valrun.is_unpublished;

    if (this.action$.value === 'unarchive') {
      condition = condition && valrun.is_archived;
    } else if (this.action$.value === 'archive') {
      condition = condition && !valrun.is_archived;
    }

    return condition;
  }

  onDataFetchError(): Observable<never> {
    this.dataFetchError.set(true);
    return EMPTY;
  }

  getInitDate(): [Date, Date] {
    // get initial date range to cover past 5 years, repeated in child...
    const today = new Date();
    const pastDate = new Date(today);
    pastDate.setFullYear(today.getFullYear() - 5);  // Subtract 5 years from the current date
    return [pastDate, today];
  }

  areFiltersApplied(): boolean {
    // check if any filters have been applied, used to define message in case of no validation results found)
    if (!this.filterPayload) {
      return false;
    }
    
    return (
      this.filterPayload.statuses.length > 0 || 
      this.filterPayload.name !== null //|| 
      //(this.filterPayload.prettyName && this.filterPayload.prettyName.length > 0)
    );
  }

}
