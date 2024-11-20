import { Component, EventEmitter, OnInit, Output } from '@angular/core';

export interface FilterPayload {
  statuses: string[];
  name: string;
  selectedDates: [Date, Date];
  prettyName: string;
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

  constructor() {
    this.updateDropdownFilters();
  }


  selectFilter() {

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
        filterValues = [this.prettyName];
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
      prettyName: this.activeFilters.find(f => f.filter === 'Dataset')?.values[0] || ''
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
