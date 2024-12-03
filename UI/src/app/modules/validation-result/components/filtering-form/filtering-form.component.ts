import {Component, model, OnInit} from '@angular/core';
import {FilterPayload} from './filterPayload.interface';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';


@Component({
  selector: 'qa-filtering-form',
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent implements OnInit {
  //
  // @Output() filterPayload = new EventEmitter<FilterPayload>();
  appliedFilters = model([] as FilterPayload[])

  // for now it's hard coded, but it's a better idea to fetch them from the model
  availableStatuses = [
    {label: 'Done', value: 'done'},
    {label: 'ERROR', value: 'error'},
    {label: 'Cancelled', value: 'cancel'},
    {label: 'Running', value: 'running'},
    {label: 'Scheduled', value: 'scheduled'},];

  filters: FilterPayload[] = [
    {name: 'Validation Name', type: "input", label: 'Type validation name', value: null},
    {name: 'Status', type: "dropdown", label: 'Select status', options: this.availableStatuses, value: null},
    {name: 'Dataset', type: "input", label: "Select dataset", value: null},
    {name: 'Submission Date', type: "calendar", label: "Select submission date", value: null},
  ];
  selectedFilter: FilterPayload = this.filters[0];
  // appliedFilters: FilterPayload[] = [];


  constructor(private datasetService: DatasetService) {
  }

  ngOnInit(): void {
    // this.updateDropdownFilters();
    // this.fetchAndLogPrettyNames();
  }

  onFilterChange(filterPayload: FilterPayload): void {
    console.log(filterPayload);
  }

  cancelFilter(filterPayload: FilterPayload): void {

  }

  addFilter(filter: FilterPayload): void {
    // console.log(filter)
    this.appliedFilters.update(filters => {
      filters.push(filter);
      return filters;
    });
    console.log(this.appliedFilters)
  }

  removeFilter(filterToBeremoved: FilterPayload): void {
    this.appliedFilters.update(filters => {
      filters.filter(filter => (filter.name !== filterToBeremoved.name));
      return filters;
    });
    // this.appliedFilters = this.appliedFilters.filter(filter => filter !== filter);
  }

  // checkIfFilterValid(filterPayload: FilterPayload): void {
  //   filterPayload
  // }

  // // get all dataset names to provide list for filter choice
  // private fetchAndLogPrettyNames(): void {
  //   this.datasetService.getAllDatasets().subscribe({
  //     next: (datasets: DatasetDto[]) => {
  //       this.availableDatasets = datasets
  //         .map(dataset => dataset.pretty_name)
  //         .filter((name, index, self) => name && self.indexOf(name) === index);
  //       console.log('Dataset Pretty Names:', this.availableDatasets);
  //     },
  //     error: (error) => {
  //       console.error('Error fetching datasets:', error);
  //     }
  //   });
  // }

  // isFilterValid(): boolean {
  //   if (this.selectedFilter === 'Dataset') {
  //     return !!(this.prettyName && (this.spatial || this.temporal || this.scaling));
  //   }
  //   if (this.selectedFilter === 'Status') {
  //     return this.selectedStatuses.length > 0;
  //   }
  //   if (this.selectedFilter === 'Submission Date') {
  //     return !!this.selectedDateRange;
  //   }
  //   return true;
  // }

  // selectFilter() {
  //
  //   if (!this.isFilterValid()) {
  //     return;
  //   }
  //   this.isEditing = false;
  //
  //   let filterValues = [];
  //   //switch case for chosen filtering variable
  //   switch (this.selectedFilter) {
  //     case 'Status':
  //       filterValues = this.selectedStatuses;
  //       break;
  //     case 'Validation Name':
  //       filterValues = [this.selectedNames];
  //       break;
  //     case 'Submission Date':
  //       filterValues = this.selectedDateRange
  //       break;
  //     case 'Dataset':
  //       filterValues.push(this.prettyName);
  //       if (this.spatial && this.temporal && this.scaling) {
  //         filterValues.push('Spatial, Temporal, or Scaling Reference');
  //       } else if (this.spatial && this.temporal) {
  //         filterValues.push('Spatial or Temporal Reference');
  //       } else if (this.spatial && this.scaling) {
  //         filterValues.push('Spatial or Scaling Reference');
  //       } else if (this.temporal && this.scaling) {
  //         filterValues.push('Temporal or Scaling Reference');
  //       } else if (this.spatial) {
  //         filterValues.push('Spatial Reference');
  //       } else if (this.temporal) {
  //         filterValues.push('Temporal Reference');
  //       } else if (this.scaling) {
  //         filterValues.push('Scaling Reference');
  //       }
  //       break;
  //   }
  //
  //   // Only actually filter if given values
  //   if (filterValues.length > 0) {
  //
  //     const existingFilterIndex = this.activeFilters.findIndex(f => f.filter === this.selectedFilter); //check if existing filter
  //
  //     if (existingFilterIndex !== -1) {
  //       this.activeFilters[existingFilterIndex].values = filterValues; // update if existing filter
  //     } else {
  //       this.activeFilters.push({ filter: this.selectedFilter, values: filterValues }); // create new if not existing
  //     }
  //
  //     this.onFilteringChange()
  //     this.availableFilters = this.availableFilters.filter(f => f !== this.selectedFilter);
  //     this.updateDropdownFilters();
  //
  //     //Reset values once filter is added
  //     this.selectedFilter = '';
  //     this.selectedStatuses = [];
  //     this.selectedNames = '';
  //     this.selectedDateRange = this.getInitDate();
  //     this.prettyName = '';
  //     this.spatial = false;
  //     this.temporal = false;
  //     this.scaling = false;
  //   }
  //   this.showFilterForm = false;
  // }

  // editFilter(index: number) {
  //
  //   this.isEditing = true;
  //   this.showFilterForm = true;
  //   const filterToEdit = this.activeFilters[index]; // get filter to edit
  //
  //   this.selectedFilter = filterToEdit.filter;
  //   this.updateDropdownFilters();
  //   this.cdr.detectChanges(); // should update drop-down to show filter being edited - doesn't seem to...
  //   console.log(this.availableFilters);
  //   switch (filterToEdit.filter) {
  //     case 'status':
  //       this.selectedStatuses = filterToEdit.values;
  //       break;
  //     case 'Validation Name':
  //       this.selectedNames = filterToEdit.values[0];
  //       break;
  //     case 'Submission Date':
  //       this.selectedDateRange = filterToEdit.values as unknown as [Date, Date]; //Not sure why this has to be converted to unkown
  //       break;
  //     case 'Dataset':
  //       this.prettyName = filterToEdit.values[0];
  //       this.spatial = filterToEdit.values.includes('Spatial Reference') || filterToEdit.values.includes('Spatial or Temporal Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
  //       this.temporal = filterToEdit.values.includes('Temporal Reference') || filterToEdit.values.includes('Spatial or Temporal Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
  //       this.scaling = filterToEdit.values.includes('Scaling Reference') || filterToEdit.values.includes('Spatial or Scaling Reference') || filterToEdit.values.includes('Temporal or Scaling Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
  //       break;
  //   }
  //
  // }

  // removeFilter(index: number) {
  //
  //   const removedFilter = this.activeFilters[index];
  //
  //   // If 'Validation Name' filter, reset to empty string to allow for filter on no name to still work
  //   if (removedFilter.filter === 'Validation Name') {
  //     this.selectedNames = '';
  //   }
  //
  //   this.availableFilters.push(this.activeFilters[index].filter); // Add deleted filter back to available filters
  //   this.activeFilters.splice(index, 1); // Remove filter from active filters
  //   this.updateDropdownFilters(); // Update list of dropdown filters
  //   this.onFilteringChange()
  // }

  // cancelFilter() {
  //   this.isEditing = false;
  //
  //   this.selectedFilter = '';
  //   this.selectedStatuses = [];
  //   this.selectedNames = '';
  //   this.selectedDateRange = this.getInitDate();
  //   this.prettyName = '';
  //   this.spatial = false;
  //   this.temporal = false;
  //   this.scaling = false;
  //
  //   this.showFilterForm = false;
  // }

  // onFilteringChange(): void {
  //   // build filter payload and emit to validation page component
  //   const filterPayload: FilterPayload = {
  //     statuses: this.activeFilters.find(f => f.filter === 'Status')?.values || [],
  //     name: this.activeFilters.find(f => f.filter === 'Validation Name')?.values[0] !== undefined ? this.activeFilters.find(f => f.filter === 'Validation Name')?.values[0] : null, // need to separate null (no filter) from empty string (filter on unnamed)
  //     selectedDates: this.activeFilters.find(f => f.filter === 'Submission Date')?.values as unknown as [Date, Date] || this.getInitDate(),
  //     prettyName: this.activeFilters.find(f => f.filter === 'Dataset')?.values[0] || '',
  //     spatialReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false,
  //     temporalReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false,
  //     scalingReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Temporal or Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false
  //   };
  //   this.filterPayload.emit(filterPayload);
  // }

  //
  // updateDropdownFilters() {
  //   this.dropdownFilters = this.allFilters
  //     .filter(filter => {
  //       // console.log(this.isEditing, filter, this.selectedFilter);
  //       if (this.isEditing && filter === this.selectedFilter) {
  //         return true;
  //       }
  //       return !this.activeFilters.some(af => af.filter === filter);
  //     })
  //     .map(filter => ({
  //       label: filter,
  //       value: filter
  //     }));
  // }
  //
  // getInitDate(): [Date, Date] {
  //   // Set an initial date range to cover past 5 years
  //   const today = new Date();
  //   const pastDate = new Date(today);
  //   pastDate.setFullYear(today.getFullYear() - 5);
  //   return [pastDate, today];
  // }

}
