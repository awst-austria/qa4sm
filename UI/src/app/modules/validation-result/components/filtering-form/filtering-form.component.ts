import {Component, input, model, OnInit} from '@angular/core';
import {FilterConfig} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {Observable, of} from "rxjs";
import {map} from "rxjs/operators";

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
  //
  // allFilters = Object.keys(this.FILTER_CONFIGS);
  // availableFilters = [...this.allFilters];

  selectedFilterKey: string | null = null; // key of filter config
  selectedFilter: FilterConfig;


  activeFilters: { filter: string, values: string[] }[] = []; // active filters and their values
  filterStates: { [key: string]: FilterState } = {}; // current/runtime values of filters
  dropdownFilters: { label: string, value: string }[] = []; // filters still available after applied ones are removed from list
  isEditing: boolean = false; //to define if editing filter, required to properly show filter in dropdown when editing active filter


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


    // // get all dataset names to provide list for filter choice
    // this.availableDatasetsSignal().subscribe({
    //     next: (datasets: DatasetDto[]) => {
    //         const prettyNames = datasets
    //             .map(dataset => dataset.pretty_name);
    //             ['spatialRef', 'temporalRef', 'scalingRef'].forEach(field => {
    //             this.FILTER_CONFIGS.find(filter => filter.name === field).options = prettyNames;
    //         })
    //     }
    // });
  }


  // isFilterValid(): boolean {
  //     // check the validity of the given filter input using its validation function
  //     if (!this.selectedFilterKey) return false;
  //     return this.FILTER_CONFIGS[this.selectedFilterKey]
  //         .validationFn(this.filterStates[this.selectedFilterKey]);
  // }
  //
  // addFilter() {
  //   // Check if filter is valid and add it to active filters
  //   // if (!this.isFilterValid()) return;
  //   const config = this.FILTER_CONFIGS[this.selectedFilterKey];
  //   const filterValues = config.formatValuesFn(this.filterStates[this.selectedFilterKey]);
  //
  //   // this.updateActiveFilters(filterValues);
  //   // this.onFilteringChange();
  //   // this.resetFilterState();
  //   // this.updateDropdownFilters()
  // }

  private updateActiveFilters(filterValues: string[]) {
    // update active filters with new filter values, either adding new filter or updating existing one
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

  // private resetFilterState() {
  //   // reset filter state after successfully adding filter
  //   this.filterStates[this.selectedFilterKey] = {
  //     value: null,
  //   };
  //   this.selectedFilterKey = null;
  //   // this.updateDropdownFilters();
  // }

  // private getFilterValues(filterName: string): string[] {
  //   const filter = this.activeFilters.find(f => f.filter === filterName);
  //   return filter ? filter.values : [];
  // }

  onFilteringChange(): void {
    // build filter payload and emit to validation page component

    //////// neeeds to be made more generic ///////////
    // const filterPayload: FilterPayload = {
    //   statuses: this.getFilterValues('Status'),
    //   name: this.getFilterValues('Validation Name')[0],
    //   start_time: this.getFilterValues('Submission Date')[0],
    //   spatialRef: this.getFilterValues('Spatial Reference Dataset'),
    //   temporalRef: this.getFilterValues('Temporal Reference Dataset'),
    //   scalingRef: this.getFilterValues('Scaling Reference Dataset')
    // };
    //this.filterPayload.emit(filterPayload);
    // this.filterService.updateFilters(filterPayload);

  }

  // cancelFilter() {
  //     // cancel filter input form and reset state
  //     this.isEditing = false;
  //     this.resetFilterState()
  // }

  // editFilter(index: number) {
  //     // edit filter by setting filter form to show and setting selected filter key to filter being edited
  //     this.isEditing = true;
  //     const filterToEdit = this.activeFilters[index];
  //     this.selectedFilterKey = filterToEdit.filter;
  //     this.updateDropdownFilters();
  // }

  // removeFilter(index: number) {
  //     // remove filter from active filters and add it back to available filters to update dropdown list
  //     const removedFilter = this.activeFilters[index];
  //     this.availableFilters.push(this.activeFilters[index].filter);
  //     this.activeFilters.splice(index, 1);
  //     this.updateDropdownFilters();
  //     this.onFilteringChange()
  // }

  // updateDropdownFilters() {
  //     // update dropdown filter list to show filters that are not active
  //     const availableFilters = Object.keys(this.FILTER_CONFIGS)
  //         .filter(filter => {
  //             return (this.isEditing && filter === this.selectedFilterKey) ||
  //                 !this.activeFilters.some(af => af.filter === filter);
  //         });
  //
  //     this.dropdownFilters = availableFilters.map(filter => ({
  //         label: filter,
  //         value: filter
  //     }));
  //
  // }

  cleanFilters(): void {
    this.validationFilters.set([]);
  }

  addFilter() {
    this.validationFilters.update(filters => {
        if (!filters.find(filter => filter.name === this.selectedFilter.name)) {
          filters.push(this.selectedFilter);
        }
        return filters;
      }
    )
    console.log(this.validationFilters())
  }

  filterValidations() {
    console.log('I am trying filtering your validations')
  }

  removeFilter(filterToRemove: FilterConfig) {
    this.validationFilters.update(filters => {
      return filters.filter(filter => filter.name !== filterToRemove.name);
    });
  }
}
