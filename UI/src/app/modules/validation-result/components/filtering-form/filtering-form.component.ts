import {Component, input, model, OnInit} from '@angular/core';
import {FilterConfig, FilterPayload} from './filter-payload.interface';

import {DatasetDto} from 'src/app/modules/core/services/dataset/dataset.dto';
import {FilterService} from 'src/app/modules/validation-result/services/filter.service';
import {Observable} from "rxjs";

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

    public readonly FILTER_CONFIGS: FilterConfig[] = [
        {
            name: 'Status',
            type: 'multi-select',
            options: ['Done', 'ERROR', 'Cancelled', 'Running', 'Scheduled'], // at some point it should be fetched from backend
            validationFn: (state: FilterState) => {
                return Array.isArray(state?.value) && state.value.length > 0
            },
            formatValuesFn: (state: FilterState) => state.value,
            backendField: 'statuses',
            value: [],
        },
        {
            name: 'Validation Name',
            type: 'string-input',
            validationFn: (state: FilterState) => true,
            formatValuesFn: (state: FilterState) => [state.value],
            backendField: 'name',
            value: [],
        },
        {
            name: 'Submission Date',
            type: 'date-input',
            validationFn: (state: FilterState) => true,
            formatValuesFn: (state: FilterState) => {
                const date = state.value as Date;
                return [date.toLocaleDateString()];
            },
            backendField: 'start_time',
            value: [],
        },
        {
            name: 'Spatial Reference Dataset',
            type: 'multi-select',
            options: [],
            validationFn: (state: FilterState) => {
                return Array.isArray(state?.value) && state.value.length > 0
            },
            formatValuesFn: (state: FilterState) => state.value,
            backendField: 'spatialRef',
            value: [],
        },
        {
            name: 'Temporal Reference Dataset',
            type: 'multi-select',
            options: [],
            validationFn: (state: FilterState) => {
                return Array.isArray(state?.value) && state.value.length > 0
            },
            formatValuesFn: (state: FilterState) => state.value,
            backendField: 'temporalRef',
            value: [],
        },
        {
            name: 'Scaling ref dataset',
            type: 'multi-select',
            options: [],
            validationFn: (state: FilterState) => {
                return Array.isArray(state?.value) && state.value.length > 0
            },
            formatValuesFn: (state: FilterState) => state.value,
            backendField: 'scalingRef',
            value: [],
        }
    ];


    availableDatasets: string[] = [];
    allFilters = Object.keys(this.FILTER_CONFIGS);
    availableFilters = [...this.allFilters];

    selectedFilter: string | null = null; // key of filter config
    activeFilters: { filter: string, values: string[] }[] = []; // active filters and their values
    filterStates: { [key: string]: FilterState } = {}; // current/runtime values of filters
    dropdownFilters: { label: string, value: string }[] = []; // filters still available after applied ones are removed from list
    isEditing: boolean = false; //to define if editing filter, required to properly show filter in dropdown when editing active filter


    constructor(private filterService: FilterService) {
        Object.keys(this.FILTER_CONFIGS).forEach(key => {
            this.filterStates[key] = {
                value: null,
            };
        });
        this.updateDropdownFilters();
    }


    ngOnInit(): void {
        this.validationFilters.set(this.FILTER_CONFIGS)
        this.fetchPrettyNames();
    }

    private fetchPrettyNames(): void {
        // get all dataset names to provide list for filter choice
        this.availableDatasetsSignal().subscribe({
            next: (datasets: DatasetDto[]) => {
                this.availableDatasets = datasets
                    .map(dataset => dataset.pretty_name)
                this.FILTER_CONFIGS['Spatial Reference Dataset'].options = this.availableDatasets;  // should change these so not hardcoded
                this.FILTER_CONFIGS['Temporal Reference Dataset'].options = this.availableDatasets;
                this.FILTER_CONFIGS['Scaling Reference Dataset'].options = this.availableDatasets;
            }
        });
    }


    get filterConfigs() {
        // get the filters
        return this.FILTER_CONFIGS;
    }

    isFilterValid(): boolean {
        // check the validity of the given filter input using its validation function
        if (!this.selectedFilter) return false;
        return this.FILTER_CONFIGS[this.selectedFilter]
            .validationFn(this.filterStates[this.selectedFilter]);
    }

    addFilter() {
        // Check if filter is valid and add it to active filters
        if (!this.isFilterValid()) return;
        const config = this.FILTER_CONFIGS[this.selectedFilter];
        const filterValues = config.formatValuesFn(this.filterStates[this.selectedFilter]);

        this.updateActiveFilters(filterValues);
        this.onFilteringChange();
        this.resetFilterState();
        this.updateDropdownFilters()
    }

    private updateActiveFilters(filterValues: string[]) {
        // update active filters with new filter values, either adding new filter or updating existing one
        const existingIndex = this.activeFilters
            .findIndex(f => f.filter === this.selectedFilter);
        if (existingIndex !== -1) {
            this.activeFilters[existingIndex].values = filterValues;
        } else {
            this.activeFilters.push({
                filter: String(this.selectedFilter),
                values: filterValues
            });
        }
    }

    private resetFilterState() {
        // reset filter state after successfully adding filter
        this.filterStates[this.selectedFilter] = {
            value: null,
        };
        this.selectedFilter = null;
        this.updateDropdownFilters();
    }

    private getFilterValues(filterName: string): string[] {
        const filter = this.activeFilters.find(f => f.filter === filterName);
        return filter ? filter.values : [];
    }

    onFilteringChange(): void {
        // build filter payload and emit to validation page component

        //////// neeeds to be made more generic ///////////
        const filterPayload: FilterPayload = {
            statuses: this.getFilterValues('Status'),
            name: this.getFilterValues('Validation Name')[0],
            start_time: this.getFilterValues('Submission Date')[0],
            spatialRef: this.getFilterValues('Spatial Reference Dataset'),
            temporalRef: this.getFilterValues('Temporal Reference Dataset'),
            scalingRef: this.getFilterValues('Scaling Reference Dataset')
        };
        //this.filterPayload.emit(filterPayload);
        this.filterService.updateFilters(filterPayload);

    }

    cancelFilter() {
        // cancel filter input form and reset state
        this.isEditing = false;
        this.resetFilterState()
    }

    editFilter(index: number) {
        // edit filter by setting filter form to show and setting selected filter key to filter being edited
        this.isEditing = true;
        const filterToEdit = this.activeFilters[index];
        this.selectedFilter = filterToEdit.filter;
        this.updateDropdownFilters();
    }

    removeFilter(index: number) {
        // remove filter from active filters and add it back to available filters to update dropdown list
        const removedFilter = this.activeFilters[index];
        this.availableFilters.push(this.activeFilters[index].filter);
        this.activeFilters.splice(index, 1);
        this.updateDropdownFilters();
        this.onFilteringChange()
    }

    updateDropdownFilters() {
        // update dropdown filter list to show filters that are not active
        const availableFilters = Object.keys(this.FILTER_CONFIGS)
            .filter(filter => {
                return (this.isEditing && filter === this.selectedFilter) ||
                    !this.activeFilters.some(af => af.filter === filter);
            });

        this.dropdownFilters = availableFilters.map(filter => ({
            label: filter,
            value: filter
        }));

    }
}
