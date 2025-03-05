import {Component, input, model, signal} from '@angular/core';
import {FilterConfig} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {Observable, of} from "rxjs";

@Component({
  selector: 'qa-filtering-form',
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent {

  validationFilters = model<FilterConfig[]>()
  availableDatasetsSignal = input<Observable<DatasetDto[]>>();

  panelCollapsed = signal<boolean>(true);  // Signal to manage the panel's collapsed state
  loading = signal<boolean>(false);  // Signal to manage loading state
  error = signal<string | null>(null);  // Signal to manage error state

  public readonly FILTER_CONFIGS: FilterConfig[] = [
    {
      name: 'validationStatuses',
      label: 'Validation Status',
      backendName: 'status',
      optionPlaceHolder: 'Select statuses',
      type: 'multi-select',
      options: of(['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled']), // at some point it should be fetched from backend
    },
    {
      name: 'validationName',
      label: 'Validation Name',
      backendName: 'name',
      optionPlaceHolder: 'Enter validation name',
      type: 'string',
      selectedOptions: []
    },
    {
      name: 'startTime',
      label: 'Submission Date',
      optionPlaceHolder: 'Select date',
      backendName: 'start_time',
      type: 'date',
      selectedOptions: []
    },
    {
      name: 'spatialRef',
      label: 'Spatial Reference Dataset',
      backendName: 'spatial_reference',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: []
    },
    {
      name: 'temporalRef',
      label: 'Temporal Reference Dataset',
      backendName: 'temporal_reference',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: []
    },
    {
      name: 'scalingRef',
      label: 'Scaling Reference Dataset',
      backendName: 'scaling_reference',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: []
    }
  ];

  selectedFilter: FilterConfig;


  updateFilters(): void {
    this.validationFilters.update(filters => {
      // Create a new array for filters
      const updatedFilters = [...filters];
      const filterForUpdate = updatedFilters.find(filter => filter.name === this.selectedFilter.name);

      if (filterForUpdate) {
        // Remove filter if multi-select has no selected options
        if (filterForUpdate.type === 'multi-select' && filterForUpdate.selectedOptions.length === 0) {
          return updatedFilters.filter(filter => filter.name !== filterForUpdate.name);
        } else {
          // Create a new object for the updated filter to ensure immutability
          const newFilter = {...filterForUpdate, selectedOptions: [...this.selectedFilter.selectedOptions]};
          return updatedFilters.map(filter => filter.name === newFilter.name ? newFilter : filter);
        }
      } else {
        // Add a new filter by creating a new object
        const newFilter = {...this.selectedFilter, selectedOptions: [...this.selectedFilter.selectedOptions]};
        updatedFilters.push(newFilter);
      }

      return updatedFilters;
    });
  }

  addOption(): void {
    // For multiselect this step is done automatically, because the ngModel updates selected options
    if (this.selectedFilter && this.selectedFilter.value) {
      // Create a new selectedOptions array to ensure immutability
      this.selectedFilter.selectedOptions = [...this.selectedFilter.selectedOptions, this.selectedFilter.value];
      this.updateFilters();
    }
  }

  removeOption(filter: FilterConfig, option: any): void {
    filter.selectedOptions = filter.selectedOptions.filter(opt => opt !== option);
    if (filter.selectedOptions.length === 0) {
      this.removeFilter(filter);
    }
  }

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

}
