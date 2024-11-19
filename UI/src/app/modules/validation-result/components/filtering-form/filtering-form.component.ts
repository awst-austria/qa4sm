import { Component, EventEmitter, OnInit, Output } from '@angular/core';

export interface FilterPayload {
  statuses: string[];
  name: string;
  selectedDates: [Date, Date];
}


@Component({
  selector: 'qa-filtering-form',
  //standalone: false,
  //imports: [],
  templateUrl: './filtering-form.component.html',
  styleUrl: './filtering-form.component.scss'
})
export class FilteringFormComponent {

  @Output() filterPayload =  new EventEmitter<FilterPayload>();


  availableStatuses = ['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled']
  selectedFilter: string = '';
  activeFilters: { filter: string, values: string[] }[] = [];
  availableFilters = ['name', 'Status', 'Date'];
  dropdownFilters: { label: string, value: string }[] = []; // filters still available after applied ones are removed from list

  selectedStatuses: string[] = []; 
  selectedNames: string = ''; 
  selectedDateRange: [Date | null, Date | null];

  constructor() {
    this.updateDropdownFilters();
  }


  selectFilter() {
    let filterValues = [];

    //
    switch (this.selectedFilter) {
      case 'Status':
        filterValues = this.selectedStatuses;
        break;
      case 'name':
        filterValues = [this.selectedNames];
        break;
      case 'Date':
        filterValues = this.selectedDateRange
        break;
    }
    
    // Only actually filter if given values 
    if (filterValues.length > 0) {
      const existingFilterIndex = this.activeFilters.findIndex(f => f.filter === this.selectedFilter);
      const newFilter = { filter: this.selectedFilter, values: filterValues };

      if (existingFilterIndex !== -1) {
        this.activeFilters[existingFilterIndex].values = filterValues;
      } else {
        this.activeFilters.push({ filter: this.selectedFilter, values: filterValues });
      }

      this.onFilteringChange()
      this.availableFilters = this.availableFilters.filter(f => f !== this.selectedFilter);
      this.updateDropdownFilters();

      this.selectedFilter = '';
      this.selectedStatuses = [];
      this.selectedNames = '';
      //this.selectedDateRange = [, ];
    }
  }

  editFilter(index: number) {
    const filterToEdit = this.activeFilters[index];

    this.selectedFilter = filterToEdit.filter;
    switch (filterToEdit.filter) {
      case 'status':
        this.selectedStatuses = filterToEdit.values;
        break;
      case 'name':
        this.selectedNames = filterToEdit.values[0];
        break;
    }
    this.selectedFilter = filterToEdit.filter;
  }

  removeFilter(index: number) {
    this.availableFilters.push(this.activeFilters[index].filter);
    this.activeFilters.splice(index, 1);
    this.updateDropdownFilters();
    this.onFilteringChange()
  }

  onFilteringChange(): void{


    const filterPayload : FilterPayload = {statuses: this.selectedStatuses, name: this.selectedNames, selectedDates:this.selectedDateRange}
    this.filterPayload.emit(filterPayload);
  }  

  updateDropdownFilters() {
    this.dropdownFilters = this.availableFilters.map(f => ({ label: f, value: f }));
  }

}
