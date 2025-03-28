import {Component, computed, effect, HostListener, input, OnInit, signal} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {HttpParams} from '@angular/common/http';
import {EMPTY, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {FilterConfig,} from 'src/app/modules/validation-result/components/filtering-form/filter-payload.interface';
import {DatasetService} from "../../../core/services/dataset/dataset.service";
import {DatasetDto} from "../../../core/services/dataset/dataset.dto";
import {DatasetVersionService} from "../../../core/services/dataset/dataset-version.service";
import {DatasetVariableService} from "../../../core/services/dataset/dataset-variable.service";
import {DatasetVersionDto} from "../../../core/services/dataset/dataset-version.dto";
import {DatasetVariableDto} from "../../../core/services/dataset/dataset-variable.dto";
import {
  getDefaultValidationActionState,
  MultipleValidationAction
} from "../handle-multiple-validations/multiple-validation-action";

@Component({
  selector: 'qa-validation-page-paginated',
  templateUrl: './validation-page-paginated.component.html',
  styleUrls: ['./validation-page-paginated.component.scss']
})
export class ValidationPagePaginatedComponent implements OnInit {
  published = input<boolean>();
  validations: ValidationrunDto[] = [];
  // the variable below stores information about the number of all validations run by the user. validations.length
  // provides information about how many validations are actually displayed
  numberOfUserValidations: number;

  // valFilters: FilterConfig[] = [];  // Updated to signal
  valFilters = signal<FilterConfig[]>([]);  // Updated to signal

  maxNumberOfPages: number;
  currentPage = 1;
  limit = 10;
  offset = 0;
  order = signal('start_time:desc');

  isLoading: boolean = false;
  orderChange: boolean = false;
  endOfPage: boolean = false;

  datasets$: Observable<DatasetDto[]>;
  versions$: Observable<DatasetVersionDto[]>;
  variables$: Observable<DatasetVariableDto[]>;

  multipleValidationAction: MultipleValidationAction = getDefaultValidationActionState();

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
    this.datasets$ = this.datasetService.getAllDatasets(true, false);
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
      this.offset = (this.currentPage - 1) * this.limit;
      this.getValidationsAndItsNumber(true);
    }
  }

  getHttpParams(): HttpParams {
    let parameters = new HttpParams()
      .set('offset', String(this.offset))
      .set('limit', String(this.limit))
      .set('order', String(this.order()));

    this.valFilters().forEach(filter => {
      parameters = parameters.set('filter:' + filter.backendName, filter.selectedOptions().toString());
    });
    return parameters;
  }


  getValidationsAndItsNumber(onScroll = false): void {
    this.isLoading = true;
    const parameters = computed(() => this.getHttpParams());
    const validationSet$ = this.published()
      ? this.validationrunService.getPublishedValidationruns(parameters())
      : this.validationrunService.getMyValidationruns(parameters());

    validationSet$.pipe(
      catchError(() => this.onDataFetchError())
    )
      .subscribe(
        response => {
          this.handleFetchedValidations(response, onScroll);
        });
  }

  handleFetchedValidations(serverResponse: {
    validations: ValidationrunDto[];
    length: number;
  }, onScroll: boolean): void {

    this.numberOfUserValidations = serverResponse.length;
    this.maxNumberOfPages = Math.ceil(serverResponse.length / this.limit);

    if (!onScroll || this.orderChange) {
      if (!this.orderChange){
        this.currentPage = 1; // Reset to the first page
        this.endOfPage = false;
      }
      this.validations = serverResponse.validations;
    } else {
      if (serverResponse.validations.length) {
        this.validations = this.validations.concat(serverResponse.validations);
        this.checkIfValidationShouldBeSelected();

        if (this.currentPage >= this.maxNumberOfPages || serverResponse.validations.length < this.limit) {
          this.setEndOfPage();
        }
      } else {
        this.setEndOfPage();
      }
    }
    this.orderChange = false;
    this.isLoading = false;
  }

  checkIfValidationShouldBeSelected() {
    if (this.multipleValidationAction.allSelected) {
      this.multipleValidationAction.selectedValidationIds = this.validations
        .filter(val => this.checkIfActionApplies(val))
        .map(val => val.id);
    }
  }

  getOrder(order): void {
    this.order.set(order);
    this.orderChange = true;
  }

  setEndOfPage() {
    this.endOfPage = true;
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
    const parameters = this.getHttpParams();
    this.currentPage = 1; // Reset to the first page


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

  updateSelectedValidations(checked: string[], id: string): void {
    let selectedValidations = this.multipleValidationAction.selectedValidationIds;
    if (checked.includes(id)) {
      selectedValidations = [...selectedValidations, id];
    } else {
      selectedValidations = selectedValidations.filter((selectedId: string) => selectedId !== id);
    }
    this.multipleValidationAction.selectedValidationIds = selectedValidations;
  }

  checkIfActionApplies(valrun: ValidationrunDto): boolean {
    return (this.multipleValidationAction.action === 'unarchive') ? valrun.is_unpublished && valrun.is_archived : !valrun.is_archived;
  }

  onDataFetchError(): Observable<never> {
    this.dataFetchError.set(true);
    return EMPTY;
  }
}
