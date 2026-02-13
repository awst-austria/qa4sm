import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { Observable, BehaviorSubject, combineLatest, of, Subscription } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, map, shareReplay, startWith, tap, switchMap, take, filter } from 'rxjs/operators';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';

// PrimeNG
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { TooltipModule } from 'primeng/tooltip';

// Services
import { ValidationRunFacade } from '../../modules/core/services/validation-run/validationrun.facade';
import { AuthService } from '../../modules/core/services/auth/auth.service';
import { ToastService } from 'src/app/modules/core/services/toast/toast.service';

interface SortState {
  field: string;
  order: number;
}

@Component({
  selector: 'qa-published-validations',
  standalone: true,
  imports: [
    ButtonModule, CommonModule, RouterModule, TableModule,
    TooltipModule, InputTextModule, DatePickerModule,
    FloatLabelModule, FormsModule, ReactiveFormsModule
  ],
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss'],
})
export class PublishedValidationsComponent implements OnInit, OnDestroy {
  // Streams from Facade
  loading$ = this.facade.loading$;
  isLogged$ = this.authService.authenticated;
  dataFetchError = false;

  // Calculate pinned validations
  pinnedIds = new Set<string>();
  private authSub?: Subscription;

  // Main data streams for the template
  rows$!: Observable<any[]>;
  totalRecords$!: Observable<number>;

  filterForm!: FormGroup;
  
  // UI State Subjects
  private page$ = new BehaviorSubject({ page: 0, rows: 20 });
  private sort$ = new BehaviorSubject<SortState>({ field: 'start_time', order: -1 });

  constructor(
    private fb: FormBuilder,
    private facade: ValidationRunFacade,
    private authService: AuthService,
    private router: Router,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    // Initialize search filters
    this.filterForm = this.fb.group({
      dateRange: [null],
      name: [''],
      dataset: ['']
    });

    // 1. Create a stream of filter changes
    const filters$ = this.filterForm.valueChanges.pipe(
      startWith(this.filterForm.value),
      debounceTime(300),
      // Only trigger if actual values changed
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      // Reset to first page on any filter change
      tap(() => this.page$.next({ ...this.page$.value, page: 0 }))
    );

    // 2. Main Orchestrator: Combine Filters, Pagination, and Sorting
    const dataState$ = combineLatest([filters$, this.page$, this.sort$]).pipe(
      switchMap(([f, p, s]) => {
        // Use the centralized logic from Facade to build API params
        const params = this.facade.ValidationRunFilters(f, p, s);
        
        return this.facade.getValidations('published', params).pipe(
          catchError((err) => {
            console.error('Fetch error:', err);
            this.dataFetchError = true;
            return of({ rows: [], total: 0 });
          })
        );
      }),
      // Share results to avoid multiple HTTP calls for rows$ and totalRecords$
      shareReplay(1)
    );

    // Bind streams for the template
    this.rows$ = dataState$.pipe(map(res => res.rows));
    this.totalRecords$ = dataState$.pipe(map(res => res.total));

    // Subscribe pinned validations
    this.authSub = this.authService.authenticated
      .pipe(filter(Boolean))
      .subscribe(() => {
        const copied = this.authService.currentUser?.copied_runs ?? [];
        this.pinnedIds = new Set(copied.map(String));
      });
  }

  // Checks if the validation run is already in user's list (pinned)
  isPinned(row: any): boolean {
    return this.pinnedIds.has(String(row.id));
  }

  //Handles Pin/Unpin action
  onTogglePin(row: any, event: Event): void {
    event.stopPropagation();

    const id = String(row.id);
    const wasPinned = this.pinnedIds.has(id);
    const label = row.name_tag?.trim() || row.id;

    // 1) Change pinned/unpinned button
    if (wasPinned) this.pinnedIds.delete(id);
    else this.pinnedIds.add(id);

    // 2) Update pinned state on the server
    this.facade.togglePin(row.id, wasPinned).pipe(take(1)).subscribe({
      next: () => {
        this.toastService.showSuccessWithHeader(
          'Success',
          wasPinned ? `Unpinned "${label}".` : `Pinned "${label}" to my validations page.`
        );

        this.authService.init();
      },
      error: (err) => {
        console.error('Pin error:', err);

        // 4) rollback
        if (wasPinned) this.pinnedIds.add(id);
        else this.pinnedIds.delete(id);

        this.toastService.showErrorWithHeader(
          'Error',
          wasPinned ? 'Could not unpin validation.' : 'Could not pin validation.'
        );
      }
    });
  }

  // PrimeNG Table Event Handlers
  onPageChange(event: any): void {
    this.page$.next({ page: event.first / event.rows, rows: event.rows });
  }

  onSortChange(event: any): void {
    this.sort$.next({ field: event.field, order: event.order });
  }

  // View Results page
  ViewResults(row: any) {
    this.router.navigate(['/validation-result', row.id]);
  }

  ngOnDestroy(): void {
    this.authSub?.unsubscribe();
  }

}