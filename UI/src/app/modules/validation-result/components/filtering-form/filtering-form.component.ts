import {Component, input, model, OnInit, signal} from '@angular/core';
import {FilterConfig} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {Observable, of} from "rxjs";
import {catchError, debounceTime, map} from "rxjs/operators";

interface FilterState {
  // contains the runtime values of filters
  value: any;
}


@Component({
  selector: 'qa-filtering-form',
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent implements OnInit {

  validationFilters = model<FilterConfig[]>()
  availableDatasetsSignal = input<Observable<DatasetDto[]>>();

  panelCollapsed = signal<boolean>(true);  // Signal to manage the panel's collapsed state
  loading = signal<boolean>(false);  // Signal to manage loading state
  error = signal<string | null>(null);  // Signal to manage error state


  public FILTER_CONFIGS: FilterConfig[] = [
    {
      name: 'validationStatuses',
      label: 'Validation Status',
      optionPlaceHolder: 'Select statuses',
      type: 'multi-select',
      options: of(['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled']), // at some point it should be fetched from backend
    },
    {
      name: 'validationName',
      label: 'Validation Name',
      optionPlaceHolder: 'Enter validation name',
      type: 'string',
    },
    {
      name: 'startTime',
      label: 'Submission Date',
      optionPlaceHolder: 'Select date',
      type: 'date',
    },
    {
      name: 'spatialRef',
      label: 'Spatial Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'multi-select',
      options: [],
    },
    {
      name: 'temporalRef',
      label: 'Temporal Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'multi-select',
      options: [],
    },
    {
      name: 'scalingRef',
      label: 'Scaling Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'multi-select',
      options: [],
    }
  ];

  selectedFilterKey: string | null = null; // key of filter config
  selectedFilter: FilterConfig;


  activeFilters: { filter: string, values: string[] }[] = []; // active filters and their values


  constructor() {
  }


  ngOnInit(): void {
    // this.validationFilters.set(this.FILTER_CONFIGS)
    this.fetchPrettyNames();
  }

  private fetchPrettyNames(): void {
    const prettyNames = this.availableDatasetsSignal().pipe(
      map(dataset => dataset.map(item => item.pretty_name))
    );

    ['spatialRef', 'temporalRef', 'scalingRef'].forEach(field => {
      this.FILTER_CONFIGS.find(filter => filter.name === field).options = prettyNames;
    })

  }

  cleanFilters(): void {
    this.selectedFilter = null;
    this.validationFilters.set([]);
  }

  // addFilter() {
  //   this.validationFilters.update(filters => {
  //       if (!filters.find(filter => filter.name === this.selectedFilter.name)) {
  //         filters.push(this.selectedFilter);
  //       }
  //       return filters;
  //     }
  //   )
  // }

  addFilter(): void {
    this.validationFilters.update(filters => {
      const filterForUpdate = filters.find(filter => filter.name === this.selectedFilter.name)

      if (!filterForUpdate) {
        filters.push(this.selectedFilter);
      } else if (filterForUpdate && !filterForUpdate.options) {
        console.log(filterForUpdate.value);
        // filterForUpdate.value.push()
      }
      console.log(filters, filterForUpdate)
      return filters;
    });
    this.applyFilters();
  }

  private applyFilters(): void {
    this.loading.set(true);
    this.error.set(null);

    const filterPayload = this.validationFilters().reduce((payload, filter) => {
      payload[filter.name] = filter.value;
      return payload;
    }, {});

    // Simulate backend request with debounce
    of(filterPayload).pipe(
      debounceTime(300),  // Apply debounce
      map(payload => {
        // console.log('Filter payload:', payload);
        // Simulate successful backend response
        return payload;
      }),
      catchError(err => {
        this.error.set('An error occurred while applying filters.');
        throw err;
      })
    ).subscribe({
      next: response => {
        this.loading.set(false);
        // console.log('Filters applied successfully:', response);
      },
      error: () => {
        this.loading.set(false);
      }
    });
  }



  removeFilter(filterToRemove: FilterConfig) {
    this.validationFilters.update(filters => {
      return filters.filter(filter => filter.name !== filterToRemove.name);
    });
  }

  filterValidations(): void {
    const filterPayload = this.validationFilters().reduce((payload, filter) => {
      // console.log(payload, filter)
      payload[filter.name] = filter.value;
      return payload;
    }, {});
    // console.log('Filter payload:', filterPayload);
    // Send filterPayload to the backend here
  }
}
