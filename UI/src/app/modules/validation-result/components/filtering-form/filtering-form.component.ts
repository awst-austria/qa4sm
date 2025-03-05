import {Component, input, model, signal} from '@angular/core';
import {FilterConfig} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {Observable} from "rxjs";

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
      backendName: 'status',
      label: 'Validation Status',
      optionPlaceHolder: 'Select statuses',
      type: 'multi-select',
      options: ['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled'], // at some point it should be fetched from backend
    },
    {
      backendName: 'name',
      label: 'Validation Name',
      optionPlaceHolder: 'Enter validation name',
      type: 'string',
      selectedOptions: []
    },
    {
      backendName: 'start_time',
      label: 'Submission Date',
      optionPlaceHolder: 'Select date',
      type: 'date',
      selectedOptions: []
    },
    {
      backendName: 'spatial_reference',
      label: 'Spatial Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: []
    },
    {
      backendName: 'temporal_reference',
      label: 'Temporal Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: []
    },
    {
      backendName: 'scaling_reference',
      label: 'Scaling Reference Dataset',
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
      const filterForUpdate = updatedFilters.find(filter => filter.backendName === this.selectedFilter.backendName);

      if (filterForUpdate) {
        // Remove filter if multi-select has no selected options
        if (filterForUpdate.type === 'multi-select' && filterForUpdate.selectedOptions.length === 0) {
          return updatedFilters.filter(filter => filter.backendName !== filterForUpdate.backendName);
        } else {
          // Create a new object for the updated filter to ensure immutability
          const newFilter = {...filterForUpdate, selectedOptions: [...this.selectedFilter.selectedOptions]};
          return updatedFilters.map(filter => filter.backendName === newFilter.backendName ? newFilter : filter);
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
      return filters.filter(filter => filter.backendName !== filterToRemove.backendName);
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
