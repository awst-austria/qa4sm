import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FilterPayload } from '../components/filtering-form/filterPayload.interface';

@Injectable({
  providedIn: 'root'
})
export class FilterService {

  private filterState = new BehaviorSubject<FilterPayload>({
    statuses: [],
    name: null,
    start_time: null,
    spatialRef: [],
    temporalRef: [],
    scalingRef: []
  });

  filterState$ = this.filterState.asObservable();

  updateFilters(newFilters: FilterPayload): void {
    this.filterState.next({...newFilters}); 
  }
}