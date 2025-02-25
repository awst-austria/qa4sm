import {Component, effect, HostListener, input, OnInit, signal} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {BehaviorSubject, EMPTY, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {FilterConfig,} from 'src/app/modules/validation-result/components/filtering-form/filter-payload.interface';
import {DatasetService} from "../../../core/services/dataset/dataset.service";
import {DatasetDto} from "../../../core/services/dataset/dataset.dto";
import {DatasetVersionService} from "../../../core/services/dataset/dataset-version.service";
import {DatasetVariableService} from "../../../core/services/dataset/dataset-variable.service";
import {DatasetVersionDto} from "../../../core/services/dataset/dataset-version.dto";
import {DatasetVariableDto} from "../../../core/services/dataset/dataset-variable.dto";

@Component({
  selector: 'qa-validation-page-paginated',
  templateUrl: './validation-page-paginated.component.html',
  styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
  published = input<boolean>();
  validations: ValidationrunDto[] = [];

  valFilters: FilterConfig[] = [];

  maxNumberOfPages: number;
  currentPage = 1;
  limit = 10;
  offset = 0;
  order = signal('-start_time');
  selectionActive$ = new BehaviorSubject(false);
  allSelected$ = new BehaviorSubject(false);
  action$ = new BehaviorSubject(null);
  selectedValidationIds = signal([] as string[])

  isLoading: boolean = false;
  orderChange: boolean = false;
  endOfPage: boolean = false;

  datasets$: Observable<DatasetDto[]>;
  versions$: Observable<DatasetVersionDto[]>;
  variables$: Observable<DatasetVariableDto[]>;

  // ==========================================================================================

  dataFetchError = signal(false);


  constructor(private validationrunService: ValidationrunService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService) {

    effect(() => {
        this.getValidationsAndItsNumber();
    });
  }

  ngOnInit(): void {
    this.datasets$ = this.datasetService.getAllDatasets(true, false)
    this.versions$ = this.datasetVersionService.getAllVersions();
    this.variables$ = this.datasetVariableService.getAllVariables();

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
      console.log((this.currentPage - 1) * this.limit)
      this.offset = (this.currentPage - 1) * this.limit;
      this.getValidationsAndItsNumber();
    }
  }

  getValidationsAndItsNumber(): void {
    this.isLoading = true;

    let parameters = new HttpParams()
      .set('offset', String(this.offset))
      .set('limit', String(this.limit))
      .set('order', String(this.order()));


    const validationSet$ = this.published()
      ? this.validationrunService.getPublishedValidationruns(parameters)
      : this.validationrunService.getMyValidationruns(parameters)


    validationSet$.pipe(
      catchError(() => this.onDataFetchError())
    )
      .subscribe(
        response => {
          this.handleFetchedValidations(response);
        });
  }

  handleFetchedValidations(serverResponse: { validations: ValidationrunDto[]; length: number; }): void {
    this.maxNumberOfPages = Math.ceil(serverResponse.length / this.limit);

    if (this.orderChange) {
      this.validations = serverResponse.validations;
    } else {
      if (serverResponse.validations.length) {
        this.validations = this.validations.concat(serverResponse.validations);

        this.checkIfValidationShouldBeSelected();

        if (this.validations.length < serverResponse.length) {
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

  checkIfValidationShouldBeSelected(){
    if (this.allSelected$.value) {
      const selectedValidations = [];
      const select_archived = this.action$.value === 'unarchive';
      this.validations.forEach(val => {
        if (val.is_archived === select_archived && val.is_unpublished) {
          selectedValidations.push(val.id);
        }
      })
      this.selectedValidationIds.set(selectedValidations);
    }
  }

  getOrder(order): void {
    this.order.set(order);
    this.orderChange = true;
  }

  setEndOfPage() {
    this.endOfPage = true;
    this.offset = 0;
    this.limit = this.validations.length;
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
      .set('order', String(this.order()));

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
    this.selectedValidationIds.set(event.selected.value);
    this.allSelected$.next(event.allSelected);
  }

  updateSelectedValidations(checked: string[], id: string): void {
    let selectedValidations = this.selectedValidationIds();
    if (checked.includes(id)) {
      selectedValidations = [...selectedValidations, id];
    } else {
      selectedValidations = selectedValidations.filter((selectedId: string) => selectedId !== id);
    }
    this.selectedValidationIds.set(selectedValidations);
  }

  checkIfEnabled(valrun: ValidationrunDto): boolean {
    let condition = valrun.is_unpublished && !valrun.is_archived;

    if (this.action$.value === 'unarchive') {
      condition = valrun.is_unpublished && valrun.is_archived;
    }

    return condition;
  }

  onDataFetchError(): Observable<never> {
    this.dataFetchError.set(true);
    return EMPTY;
  }


}
