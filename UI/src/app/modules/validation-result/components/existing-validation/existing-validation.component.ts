import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {EMPTY, Observable} from 'rxjs';
import {ExistingValidationDto} from '../../../core/services/validation-run/existing-validation.dto';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {Router} from '@angular/router';
import {catchError} from 'rxjs/operators';

@Component({
    selector: 'qa-existing-validation',
    templateUrl: './existing-validation.component.html',
    styleUrls: ['./existing-validation.component.scss'],
    standalone: false
})
export class ExistingValidationComponent implements OnInit {
  dateFormat = 'medium';
  timeZone = 'UTC';
   /* Visibility of p-dialog */
  visible = true;

  @Input() isThereValidation: ExistingValidationDto;
  @Output() startValidation = new EventEmitter<boolean>();
  @Output() closed = new EventEmitter<void>();

  foundValidation$: Observable<ValidationrunDto>;

  constructor(private validationService: ValidationrunService,
              private router: Router) { }

  ngOnInit(): void {

    if (!this.isThereValidation?.val_id) {
      this.visible = false;
      return;
    }

    this.foundValidation$ = this.validationService.getValidationRunById(this.isThereValidation.val_id)
      .pipe(
        catchError(() => {
          this.visible = false;
          this.startValidation.emit(true);
          return EMPTY;
        })
      );
  }
  close(): void{
    this.visible = false;
    this.closed.emit();
  }

  useAnExistingValidation(validation: ValidationrunDto): void{
    this.close(); // I need to add it, otherwise a publishing window will open, it uses the same modal window functions
    this.router.navigate([`validation-result/${validation.id}`]);
  }

  runOwnValidation(): void{
    this.close(); // I need to add it, otherwise a publishing window will open, it uses the same modal window functions
    this.startValidation.emit(true);
  }

}
