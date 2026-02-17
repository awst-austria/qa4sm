import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { Observable, BehaviorSubject, combineLatest, of, interval, Subscription} from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, map, shareReplay, startWith, tap, switchMap, take } from 'rxjs/operators';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';

// PrimeNG
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { TooltipModule } from 'primeng/tooltip';
import { TagModule } from 'primeng/tag';

// Services
import { ValidationRunFacade } from '../../modules/core/services/validation-run/validationrun.facade';
import { PinnedValidationsComponent } from 'src/app/modules/pinned-validations/pinned-validations.component';
import { ToastService } from 'src/app/modules/core/services/toast/toast.service';
import { ValidationrunService } from 'src/app/modules/core/services/validation-run/validationrun.service';
import { AuthService } from 'src/app/modules/core/services/auth/auth.service';
import { DialogModule } from 'primeng/dialog';

interface SortState {
  field: string;
  order: number;
}

@Component({
  selector: 'qa-validations',
  standalone: true,
  imports: [
    PinnedValidationsComponent, ButtonModule, CommonModule, RouterModule, 
    TableModule, TooltipModule, InputTextModule, DatePickerModule, 
    FloatLabelModule, FormsModule, ReactiveFormsModule, TagModule, DialogModule
  ],
  templateUrl: './validations.component.html',
  styleUrls: ['./validations.component.scss'],
})

export class ValidationsComponent implements OnInit, OnDestroy {
  private fb = inject(FormBuilder);
  private facade = inject(ValidationRunFacade);

  private validationrunService = inject(ValidationrunService); 
  private authService = inject(AuthService);
  private toastService = inject(ToastService);
  private router = inject(Router);

  // From Facade
  loading$ = this.facade.loading$;
  
  rows$!: Observable<any[]>;
  totalRecords$!: Observable<number>;
  dataFetchError = false;

  filterForm!: FormGroup;
  readonly PAGE_SIZE = 20;

  private page$ = new BehaviorSubject({ page: 0, rows: this.PAGE_SIZE });
  private sort$ = new BehaviorSubject<SortState>({ field: 'start_time', order: -1 });

  // Edit Validation Name
  editingRowId: string | null = null;
  tempName: string = '';

  // Display validation Progress and Status
  private statusSubscription?: Subscription;

  // For delete dialog window
  confirmDeleteVisible = false;
  deleteTarget: any | null = null;
  deleting = false;

  // For stop dialog window
  confirmStopVisible = false;
  stopTarget: any | null = null;
  stopping = false;

  ngOnInit(): void {

    // Create Filters Reactive Form with fields: dateRange, Validation-run name, Dataset name
    this.filterForm = this.fb.group({
      dateRange: [null],
      name: [''],
      dataset: ['']
    });

    // Create Observable from Reactive Form
    const filters$ = this.filterForm.valueChanges.pipe(
      startWith(this.filterForm.value),
      debounceTime(300),
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      // send to 0 page if user changed the filters
      tap(() => this.page$.next({ ...this.page$.value, page: 0 }))
    );

    // Listen to filters, page and sort and send request to backend
    const dataState$ = combineLatest([filters$, this.page$, this.sort$]).pipe(
      tap(() => this.dataFetchError = false),
      switchMap(([f, p, s]) => {
        // Filter from Facade
        const params = this.facade.ValidationRunFilters(f, p, s);
        // Use 'user' for validations loading
        return this.facade.getValidations('user', params).pipe(
          catchError(() => {
            this.dataFetchError = true;
            return of({ rows: [], total: 0 });
          })
        );
      }),
      shareReplay({ bufferSize: 1, refCount: true })
    );

    this.rows$ = dataState$.pipe(map(res => res.rows));
    this.totalRecords$ = dataState$.pipe(map(res => res.total));

    this.statusSubscription = interval(60000).pipe(
      // If we have on the page at least one running validation
      switchMap(() => this.rows$.pipe(take(1))),
      map(rows => rows.some(r => this.isLive(r)))
    ).subscribe(hasLive => {
      if (hasLive) {
        this.page$.next({ ...this.page$.value }); // page reload
      }
    });

  }

  openDeleteDialog(row: any, event: Event): void {
    event.stopPropagation();
    this.deleteTarget = row;
    this.confirmDeleteVisible = true;
  }

  closeDeleteDialog(): void {
    this.confirmDeleteVisible = false;
    this.deleteTarget = null;
  }

  confirmDelete(): void {
    if (!this.deleteTarget || this.deleting) return;

    this.deleting = true;
    const row = this.deleteTarget;

    this.validationrunService.deleteValidation(row.id).pipe(take(1)).subscribe({
      next: () => {
        this.toastService.showSuccessWithHeader('Success', 'Validation was deleted successfully.');

        this.closeDeleteDialog();
        this.page$.next({ ...this.page$.value });   // reload table
        this.authService.init();                    // refresh user if needed
        this.deleting = false;
      },
      error: () => {
        this.toastService.showErrorWithHeader(
          'Error',
          'Failed to delete validation. It might be linked to other results or you might lack permissions.'
        );
        this.deleting = false;
      }
    });
  }

  startEdit(row: any): void {
    this.editingRowId = row.id;
    this.tempName = row.name_tag || '';
  }

  cancelEdit(): void {
    this.editingRowId = null;
  }

  saveEdit(row: any): void {
    const trimmedName = this.tempName.trim();
    if (trimmedName && trimmedName !== row.name_tag) {
      this.validationrunService.saveResultsName(row.id, trimmedName).subscribe({
        next: () => {
          row.name_tag = trimmedName;
          this.editingRowId = null;
          this.toastService.showSuccessWithHeader('Success', 'Name updated');
        },
        error: () => this.toastService.showErrorWithHeader('Error', 'Update failed')
      });
    } else {
      this.editingRowId = null;
    }
  }

  // Define the status progress
  getStatusDisplay(valrun: any): { label: string, severity: string, progress?: number } {
    if (valrun.progress === 0 && valrun.end_time === null) {
      return { label: 'Scheduled', severity: 'info' };
    } else if (valrun.progress === 100 && valrun.end_time) {
      return { label: 'Done', severity: 'secondary' };
    } else if (valrun.progress === -1 || valrun.progress === -100) {
      return { label: 'Cancelled', severity: 'secondary' };
    } else if (valrun.end_time != null || valrun.total_points == 0) {
      return { label: 'Error', severity: 'danger' };
    } else {
      return { label: `Running ${valrun.progress}%`, severity: 'warning', progress: valrun.progress };
    }
  }

  // Stop Validation
  openStopDialog(row: any, event: Event): void {
    event.stopPropagation();
    this.stopTarget = row;
    this.confirmStopVisible = true;
  }

  closeStopDialog(): void {
    this.confirmStopVisible = false;
    this.stopTarget = null;
  }

  confirmStop(): void {
    if (!this.stopTarget || this.stopping) return;

    this.stopping = true;
    const row = this.stopTarget;

    this.validationrunService.stopValidation(row.id).pipe(take(1)).subscribe({
      next: () => {
        this.toastService.showSuccessWithHeader('Success', 'Validation stop requested.');
        this.closeStopDialog();
        this.page$.next({ ...this.page$.value }); // refresh table
        this.stopping = false;
      },
      error: () => {
        this.toastService.showErrorWithHeader('Error', 'Could not stop validation.');
        this.stopping = false;
      }
    });
  }

  isLive(valrun: any): boolean {
    return valrun.progress > 0 && valrun.progress < 100 && !valrun.end_time;
  }

  onPageChange(event: any): void {
    this.page$.next({ page: event.first / event.rows, rows: event.rows });
  }

  onSortChange(event: any): void {
    this.sort$.next({ field: event.field, order: event.order });
  }

  // View Results page
  ViewResults(row: any, event?: Event) {
    const target = event?.target as HTMLElement | undefined;
    if (target?.closest('button, a, input, textarea, .p-inputtext')) return;
    this.router.navigate(['/validation-result', row.id]);
  }

  ngOnDestroy(): void {
    this.statusSubscription?.unsubscribe();
  }
}