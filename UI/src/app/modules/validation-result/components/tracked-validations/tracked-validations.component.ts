import { Component, OnInit } from '@angular/core';
import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';
import { EMPTY, Observable } from 'rxjs';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { catchError } from 'rxjs/operators';
import { CustomHttpError } from '../../../core/services/global/http-error.service';
import { ToastService } from '../../../core/services/toast/toast.service';

@Component({
  selector: 'qa-tracked-validations',
  templateUrl: './tracked-validations.component.html',
  styleUrls: ['./tracked-validations.component.scss'],
  standalone: false,
})
export class TrackedValidationsComponent implements OnInit {

  constructor(private validationrunService: ValidationrunService,
              private toastService: ToastService) { }

  trackedRuns$: Observable<ValidationrunDto[]>;

  ngOnInit(): void {
    this.getData();
  }

  getData(): void{
    this.trackedRuns$ = this.validationrunService.getCustomTrackedValidations()
      .pipe(
        catchError((error: CustomHttpError) => {
          this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message);
          return EMPTY
        })
      );
  }

}
