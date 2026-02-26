import { Component, OnInit } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, shareReplay } from 'rxjs/operators';
import { ValidationrunService } from '../core/services/validation-run/validationrun.service';
import { ValidationrunDto } from '../core/services/validation-run/validationrun.dto';
import { ToastService } from '../core/services/toast/toast.service';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'qa-pinned-validations',
  standalone: true,
  imports: [CommonModule, ButtonModule, TooltipModule, RouterModule],
  templateUrl: './pinned-validations.component.html',
  styleUrl: './pinned-validations.component.scss',
})
export class PinnedValidationsComponent implements OnInit {
  pinnedValidations$!: Observable<ValidationrunDto[]>;

  constructor(
    private validationrunService: ValidationrunService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.loadPinnedValidations();
  }

  loadPinnedValidations(): void {
    this.pinnedValidations$ = this.validationrunService.getCustomTrackedValidations().pipe(
      catchError((error) => {
        console.error('Failed to load pinned validations', error);

        this.toastService.showErrorWithHeader(
          'Something went wrong',
          'Unexpected error while loading pinned validations.'
        );

        return of([] as ValidationrunDto[]);
      }),
      shareReplay({ bufferSize: 1, refCount: true })
    );
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    this.validationrunService.downloadResultFile(validationId, fileType, fileName);
  }

  unpinValidation(validationId: string): void {
    this.validationrunService.removeValidation(validationId).subscribe({
      next: () => {
        this.toastService.showSuccessWithHeader(
          'Success',
          'Validation was unpinned.'
        );

        // Reload pinned Validations
        this.loadPinnedValidations();
      },
      error: () => {
        this.toastService.showErrorWithHeader(
          'Error',
          'Failed to unpin validation.'
        );
      }
    });
  }

}
