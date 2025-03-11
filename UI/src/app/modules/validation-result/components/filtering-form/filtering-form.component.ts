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
  // z =

  public readonly FILTER_CONFIGS: FilterConfig[] = [
    {
      backendName: 'status',
      label: 'Validation Status',
      optionPlaceHolder: 'Select statuses',
      type: 'multi-select',
      options: ['DONE', 'ERROR', 'CANCELED', 'RUNNING', 'SCHEDULED'], // at some point it should be fetched from backend
      selectedOptions: signal([])
    },
    {
      backendName: 'name',
      label: 'Validation Name',
      optionPlaceHolder: 'Enter validation name',
      type: 'string',
      selectedOptions: signal([])
    },
    {
      backendName: 'start_time',
      label: 'Submission Date',
      optionPlaceHolder: 'Select date',
      type: 'date',
      selectedOptions: signal([]),
      optionParser: this.dateParser
    },
    {
      backendName: 'spatial_reference',
      label: 'Spatial Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: signal([])
    },
    {
      backendName: 'temporal_reference',
      label: 'Temporal Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: signal([])
    },
    {
      backendName: 'scaling_reference',
      label: 'Scaling Reference Dataset',
      optionPlaceHolder: 'Select datasets',
      type: 'string',
      selectedOptions: signal([])
    }
  ];

  selectedFilter: FilterConfig;

  dateParser(datesStr: string[]): string {
    let parsedDates = datesStr.map(dateStr => new Date(dateStr).toDateString());
    return parsedDates.join(',')
  }


  updateFilters(): void {
    const filters = this.validationFilters()
    const filterForUpdate = filters.find(filter => filter.backendName === this.selectedFilter.backendName);
    if (filterForUpdate) {
      //   he re I may want to either update and emmit the updated version or to remove the existing filter
      //   I want to remove the filter from the list when there is no options selected (for the input field filter, the filter can be removed with the removed button):
      if (filterForUpdate.selectedOptions().length == 0 && filterForUpdate.type === 'multi-select') {
        this.removeFilter(filterForUpdate)
      } else {
        // when not removing, refresh the filters
        this.validationFilters.set([...filters])
      }
    } else {
      this.addFilter();
    }
  }

  addFilter(): void {
    this.validationFilters.update(filters => {
      const updatedFilters = [...filters];
      updatedFilters.push(this.selectedFilter);
      return updatedFilters;
    });
  }

  onSelectedOptionsChange(newSelectedOptions: string[]): void {
    this.selectedFilter.selectedOptions.set([...newSelectedOptions]); // Update the signal with the new value
    this.updateFilters();
  }


  addOption(): void {
    // For multiselect this step is done automatically, because the ngModel updates selected options
    if (this.selectedFilter && this.selectedFilter.value) {
      let value = this.selectedFilter.value;
      if (this.selectedFilter.optionParser) {
        value = (this.selectedFilter.optionParser(this.selectedFilter.value));
      }
      // Create a new selectedOptions array to ensure immutability
      this.selectedFilter.selectedOptions.set([(value)]);
      this.updateFilters();
    }
  }

  removeFilter(filterToRemove: FilterConfig): void {
    this.validationFilters.update(filters => {
      return filters.filter(filter => filter.backendName !== filterToRemove.backendName);
    });
    this.resetFilter(filterToRemove);

  }

  private resetFilter(filter: FilterConfig): void {
    filter.value = null;
    filter.selectedOptions.set([]);
    if (this.validationFilters().length === 0) {
      this.selectedFilter = null;
    } else {
      this.selectedFilter = this.validationFilters()[0];
    }
  }

  cancelFiltering(): void {
    if (this.validationFilters().length) {
      this.selectedFilter = null;
      this.validationFilters.set([]);
      // Clean the selectedOptions of all filters
      this.FILTER_CONFIGS.forEach(this.resetFilter.bind(this));
    }
  }

}
