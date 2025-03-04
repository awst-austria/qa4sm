import {Component, input, model, OnInit, signal} from '@angular/core';
import {FilterConfig} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {Observable, of} from "rxjs";
import {catchError, debounceTime, map} from "rxjs/operators";

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

  public readonly FILTER_CONFIGS: FilterConfig[] = [
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
      selectedOptions: []
    },
    {
      name: 'startTime',
      label: 'Submission Date',
      optionPlaceHolder: 'Select date',
      type: 'date',
      selectedOptions: []
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

  selectedFilter: FilterConfig;

  ngOnInit(): void {
    this.fetchPrettyNames();
  }

  private fetchPrettyNames(): void {
    const prettyNames = this.availableDatasetsSignal().pipe(
      map(dataset => dataset.map(item => item.pretty_name))
    );

    ['spatialRef', 'temporalRef', 'scalingRef'].forEach(field => {
      const filter = this.FILTER_CONFIGS.find(filter => filter.name === field);
      if (filter) {
        filter.options = prettyNames;
      }
    });
  }



  updateFilters(): void {
    this.validationFilters.update(filters => {
      const filterForUpdate = filters.find(filter => filter.name === this.selectedFilter.name);
      if (filterForUpdate) {
        // Remove filter if multi-select has no selected options
        if (filterForUpdate.type === 'multi-select' && filterForUpdate.selectedOptions.length === 0) {
          return filters.filter(filter => filter.name !== filterForUpdate.name);
        }
      } else {
        filters.push(this.selectedFilter);
      }
      return filters;
    });
    // this.applyFilters();
  }


  //
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

  addOption(): void {
    // For multiselect this step is done automatically, because the ngModel updates selected options
    if (this.selectedFilter && this.selectedFilter.value) {
      this.selectedFilter.selectedOptions.push(this.selectedFilter.value);
      this.updateFilters();
    }
  }

  removeOption(filter: FilterConfig, option: any): void {
    filter.selectedOptions = filter.selectedOptions.filter(opt => opt !== option);
    if (filter.selectedOptions.length === 0) {
      this.removeFilter(filter);
    }
  }

  // removeFilter(filterToRemove: FilterConfig) {
  //   this.validationFilters.update(filters => {
  //     return filters.filter(filter => filter.name !== filterToRemove.name);
  //   });
  //   const filterConfig = this.FILTER_CONFIGS.find(filter => filter.name === filterToRemove.name);
  //   if (filterConfig) {
  //     filterConfig.value = null;
  //     filterConfig.selectedOptions = [];
  //   }
  //   if (this.validationFilters().length === 0) {
  //     this.selectedFilter = null;
  //   } else {
  //     this.selectedFilter = this.validationFilters()[0];
  //   }
  // }

  removeFilter(filterToRemove: FilterConfig): void {
    this.validationFilters.update(filters => {
      return filters.filter(filter => filter.name !== filterToRemove.name);
    });
    this.resetFilter(filterToRemove);
    if (this.validationFilters().length === 0) {
      this.selectedFilter = null;
    } else {
      this.selectedFilter = this.validationFilters()[0];
    }
  }

  private resetFilter(filter: FilterConfig): void {
    filter.value = null;
    filter.selectedOptions = [];
  }

  cleanFilters(): void {
    this.selectedFilter = null;
    this.validationFilters.set([]);
    // Clean the selectedOptions of all filters
    this.FILTER_CONFIGS.forEach(this.resetFilter.bind(this));
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
