import {Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FilterPayload } from './filterPayload.interface';

import { DatasetDto } from 'src/app/modules/core/services/dataset/dataset.dto';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import { filter } from 'jszip';


type FilterType = 'string-input' | 'dropdown' | 'multi-select' | 'single-select' | 'date-range' | 'dataset';

interface FilterConfig {
  name: string;
  type: FilterType;
  options?: string[];
  validationFn: (value: any) => boolean;
  formatValuesFn: (value: any) => string[];
}

interface FilterState {
  // contains the runtime values of filters
  value: any;
  //references?: {
  //  spatial: boolean;
  //  temporal: boolean;
  //  scaling: boolean;
  //};
}


@Component({
  selector: 'qa-filtering-form',
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent implements OnInit {

  public static readonly FILTER_CONFIGS: { [key: string]: FilterConfig } = {
    'Status': {
      name: 'Status',
      type: 'multi-select',
      options: ['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled'],
      validationFn: (state: FilterState) => {return Array.isArray(state?.value) && state.value.length > 0},
      formatValuesFn: (state: FilterState) => state.value
    },
    'Validation Name': {
      name: 'Validation Name', 
      type: 'string-input',
      validationFn: (state: FilterState) => true,
      formatValuesFn: (state: FilterState) => [state.value]
    },
    'Spatial Reference Dataset': {
      name: 'Spatial ref dataset', 
      type: 'multi-select',
      options: [],
      validationFn: (state: FilterState) => {return Array.isArray(state?.value) && state.value.length > 0},
      formatValuesFn: (state: FilterState) => state.value
    },
    'Temporal Reference Dataset': {
      name: 'Temporal ref dataset', 
      type: 'multi-select',
      options: [],
      validationFn: (state: FilterState) => {return Array.isArray(state?.value) && state.value.length > 0},
      formatValuesFn: (state: FilterState) => state.value
    },
    'Scaling Reference Dataset': {
      name: 'Scaling ref dataset', 
      type: 'multi-select',
      options: [],
      validationFn: (state: FilterState) => {return Array.isArray(state?.value) && state.value.length > 0},
      formatValuesFn: (state: FilterState) => state.value
    }
  };
  
  @Output() filterPayload =  new EventEmitter<FilterPayload>();

  availableDatasets: string[] = [];
  allFilters = Object.keys(FilteringFormComponent.FILTER_CONFIGS);
  availableFilters = [...this.allFilters];

  selectedFilterKey: string | null = null; // key of filter config
  activeFilters: { filter: string, values: string[] }[] = []; // active filters and their values
  filterStates: { [key: string]: FilterState } = {}; // current/runtime values of filters 
  dropdownFilters: { label: string, value: string }[] = []; // filters still available after applied ones are removed from list

  showFilterForm: boolean = false;
  isEditing: boolean = false; //to define if editing filter, required to properly show filter in dropdown when editing active filter 



  constructor(private datasetService: DatasetService) {
    Object.keys(FilteringFormComponent.FILTER_CONFIGS).forEach(key => {
      this.filterStates[key] = {
        value: null,
        //references: { spatial: false, temporal: false, scaling: false }
      };
    });
    this.updateDropdownFilters();
  }


  ngOnInit(): void {
    this.fetchAndLogPrettyNames();
  }

  // get all dataset names to provide list for filter choice
  private fetchAndLogPrettyNames(): void {
    this.datasetService.getAllDatasets().subscribe({
      next: (datasets: DatasetDto[]) => {
        this.availableDatasets = datasets
          .map(dataset => dataset.pretty_name)
          .filter((name, index, self) => name && self.indexOf(name) === index); 

        FilteringFormComponent.FILTER_CONFIGS['Spatial Reference Dataset'].options = this.availableDatasets;  // should change these so not hardcoded 
        FilteringFormComponent.FILTER_CONFIGS['Temporal Reference Dataset'].options = this.availableDatasets;
        FilteringFormComponent.FILTER_CONFIGS['Scaling Reference Dataset'].options = this.availableDatasets;
      },
      error: (error) => {
        console.error('Error fetching datasets:', error);
      }
    });
  }


  // get the filters to use in template
  get filterConfigs() {
    return FilteringFormComponent.FILTER_CONFIGS;
  }

  // check the validity of the given filter input using its validation function
  isFilterValid(): boolean {
    if (!this.selectedFilterKey) return false;

    return FilteringFormComponent.FILTER_CONFIGS[this.selectedFilterKey]
      .validationFn(this.filterStates[this.selectedFilterKey]);
  }

  selectFilter() {
    if (!this.isFilterValid()) return;
    
    const config = FilteringFormComponent.FILTER_CONFIGS[this.selectedFilterKey];
    const filterValues = config.formatValuesFn(this.filterStates[this.selectedFilterKey]);
    
    this.updateActiveFilters(filterValues);
    this.onFilteringChange();
    this.resetFilterState();
    this.showFilterForm = false;
  }

  private updateActiveFilters(filterValues: string[]) {
    const existingIndex = this.activeFilters
      .findIndex(f => f.filter === this.selectedFilterKey);
    if (existingIndex !== -1) {
      this.activeFilters[existingIndex].values = filterValues;
    } else {
      this.activeFilters.push({ 
        filter: String(this.selectedFilterKey),
        values: filterValues 
      });
    }
  }

  private resetFilterState() {
    this.filterStates[this.selectedFilterKey] = { 
      value: null, 
    };
    this.selectedFilterKey = null;
    this.showFilterForm = false;
  }

  private getFilterValues(filterName: string): string[] {
    const filter = this.activeFilters.find(f => f.filter === filterName);
    return filter ? filter.values : [];
  }

  onFilteringChange(): void { 
    // build filter payload and emit to validation page component

    //////// NEEDS TO BE UPDATED ///////////
    const filterPayload: FilterPayload = {
      statuses: this.getFilterValues('Status'),
      name: this.getFilterValues('Validation Name')[0] || null,
      spatialRef: this.getFilterValues('Spatial Reference Dataset'),
      temporalRef: this.getFilterValues('Temporal Reference Dataset'),
      scalingRef: this.getFilterValues('Scaling Reference Dataset')
    };
    ///////////////////////////////////////
    this.filterPayload.emit(filterPayload);
  }

  cancelFilter() {
    this.isEditing = false;
    this.showFilterForm = false;
    this.resetFilterState()
  }

  editFilter(index: number) {
    this.isEditing = true;
    this.showFilterForm = true;
    const filterToEdit = this.activeFilters[index]; // get filter to edit
    this.selectedFilterKey = filterToEdit.filter;
    this.updateDropdownFilters(); 
  }

  removeFilter(index: number) {
    const removedFilter = this.activeFilters[index]; 
    this.availableFilters.push(this.activeFilters[index].filter); // Add deleted filter back to available filters
    this.activeFilters.splice(index, 1); // Remove filter from active filters
    this.updateDropdownFilters(); // Update list of dropdown filters
    this.onFilteringChange()
  }

  updateDropdownFilters() {
    this.dropdownFilters = this.allFilters
      .filter(filter => {
        if (this.isEditing && filter === this.selectedFilterKey) {
          return true;
        }
        return !this.activeFilters.some(af => af.filter === filter);
      })
      .map(filter => ({
        label: filter,
        value: filter
      }));
  }
}
