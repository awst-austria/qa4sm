import { Component, EventEmitter, OnInit, Output } from '@angular/core';

export interface FilterPayload {
  statuses: string[];
  name: string;
  selectedDates: [Date, Date];
  prettyName: string;
  spatialReference: boolean;
  temporalReference: boolean;
  scalingReference: boolean;
}


@Component({
  selector: 'qa-filtering-form',
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent {

  @Output() filterPayload =  new EventEmitter<FilterPayload>();

  availableStatuses = ['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled']
  selectedFilter: string = '';
  activeFilters: { filter: string, values: string[] }[] = [];
  availableFilters = ['Validation Name', 'Status', 'Submission Date', 'Dataset'];
  dropdownFilters: { label: string, value: string }[] = []; // filters still available after applied ones are removed from list

  selectedStatuses: string[] = []; 
  selectedNames: string = ''; 
  prettyName: string = ''; 
  selectedDateRange: [Date | null, Date | null];
  spatial: boolean = false;
  temporal: boolean = false;
  scaling: boolean = false;

  constructor() {
    this.updateDropdownFilters();
  }


  selectFilter() {

    if (this.selectedFilter === 'Validation Name' && !this.selectedNames) {
      return;
    }

    // Ensure at least one of the checkboxes is selected
    if (this.selectedFilter === 'Dataset' && (!this.spatial || !this.temporal) && !this.prettyName) {
      return;
    }

    let filterValues = [];
    //switch case for chosen filtering variable
    switch (this.selectedFilter) {
      case 'Status':
        filterValues = this.selectedStatuses;
        break;
      case 'Validation Name':
        filterValues = [this.selectedNames];
        break;
      case 'Submission Date':
        filterValues = this.selectedDateRange
        break;
      case 'Dataset':
        filterValues.push(this.prettyName);
        if (this.spatial && this.temporal && this.scaling) {
          filterValues.push('Spatial, Temporal, or Scaling Reference');
        } else if (this.spatial && this.temporal) {
          filterValues.push('Spatial or Temporal Reference');
        } else if (this.spatial && this.scaling) {
          filterValues.push('Spatial or Scaling Reference');
        } else if (this.temporal && this.scaling) {
          filterValues.push('Temporal or Scaling Reference');
        } else if (this.spatial) {
          filterValues.push('Spatial Reference');
        } else if (this.temporal) {
          filterValues.push('Temporal Reference');
        } else if (this.scaling) {
          filterValues.push('Scaling Reference');
        }
        break;
    }
    


    // Only actually filter if given values 
    if (filterValues.length > 0) {

      const existingFilterIndex = this.activeFilters.findIndex(f => f.filter === this.selectedFilter); //check if existing filter 
      //const newFilter = { filter: this.selectedFilter, values: filterValues };

      if (existingFilterIndex !== -1) {
        this.activeFilters[existingFilterIndex].values = filterValues; // update if existing filter
      } else {
        this.activeFilters.push({ filter: this.selectedFilter, values: filterValues }); // create new if not existing
      }

      this.onFilteringChange()
      this.availableFilters = this.availableFilters.filter(f => f !== this.selectedFilter);
      this.updateDropdownFilters();

      //Reset values once filter is added
      this.selectedFilter = '';
      this.selectedStatuses = [];
      this.selectedNames = '';
      this.selectedDateRange = this.getInitDate();
      this.prettyName = '';
      this.spatial = false;
      this.temporal = false;
      this.scaling = false;
    }
  }

  editFilter(index: number) {

    const filterToEdit = this.activeFilters[index]; // get filter to edit
    this.selectedFilter = filterToEdit.filter; // set selected filter name

    switch (filterToEdit.filter) {
      case 'status':
        this.selectedStatuses = filterToEdit.values;
        break;
      case 'Validation Name':
        this.selectedNames = filterToEdit.values[0];
        break;
      case 'Submission Date':
        this.selectedDateRange = filterToEdit.values as unknown as [Date, Date]; //Not sure why this has to be converted to unkown
        break;
      case 'Dataset':
        this.prettyName = filterToEdit.values[0];
        this.spatial = filterToEdit.values.includes('Spatial Reference') || filterToEdit.values.includes('Spatial or Temporal Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
        this.temporal = filterToEdit.values.includes('Temporal Reference') || filterToEdit.values.includes('Spatial or Temporal Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
        this.scaling = filterToEdit.values.includes('Scaling Reference') || filterToEdit.values.includes('Spatial or Scaling Reference') || filterToEdit.values.includes('Temporal or Scaling Reference') || filterToEdit.values.includes('Spatial, Temporal, or Scaling Reference');
        break;
    }
  }

  removeFilter(index: number) {
    this.availableFilters.push(this.activeFilters[index].filter); // Add deleted filter back to available filters
    this.activeFilters.splice(index, 1); // Remove filter from active filters
    this.updateDropdownFilters(); // Update list of dropdown filters
    this.onFilteringChange()
  }

  onFilteringChange(): void {
    // build filter payload and emit to validation page component
    const filterPayload: FilterPayload = {
      statuses: this.activeFilters.find(f => f.filter === 'Status')?.values || [],
      name: this.activeFilters.find(f => f.filter === 'Validation Name')?.values[0] || '',
      selectedDates: this.activeFilters.find(f => f.filter === 'Submission Date')?.values as unknown as [Date, Date] || this.getInitDate(),
      prettyName: this.activeFilters.find(f => f.filter === 'Dataset')?.values[0] || '',
      spatialReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false,
      temporalReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Temporal Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false,
      scalingReference: this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial or Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Temporal or Scaling Reference') || this.activeFilters.find(f => f.filter === 'Dataset')?.values.includes('Spatial, Temporal, or Scaling Reference') || false
    };
    this.filterPayload.emit(filterPayload);
  }

  updateDropdownFilters() {
    this.dropdownFilters = this.availableFilters.map(f => ({ label: f, value: f }));
  }

  getInitDate(): [Date, Date] {
    // Set an initial date range to cover past 5 years 
    const today = new Date();
    const pastDate = new Date(today);
    pastDate.setFullYear(today.getFullYear() - 5);  
    return [pastDate, today];
  }

}
