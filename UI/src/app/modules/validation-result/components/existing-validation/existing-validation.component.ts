import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ModalWindowService } from '../../../core/services/global/modal-window.service';
import { EMPTY, Observable } from 'rxjs';
import { ExistingValidationDto } from '../../../core/services/validation-run/existing-validation.dto';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'qa-existing-validation',
  templateUrl: './existing-validation.component.html',
  styleUrls: ['./existing-validation.component.scss'],
  standalone: false,
})
export class ExistingValidationComponent implements OnInit {
  dateFormat = 'medium';
  timeZone = 'UTC';
  display$: Observable<'open' | 'close'>;
  @Input() isThereValidation: ExistingValidationDto;
  @Output() startValidation = new EventEmitter<boolean>();

  foundValidation$: Observable<ValidationrunDto>;
  constructor(private modalService: ModalWindowService,
              private validationService: ValidationrunService,
              private router: Router) { }

  ngOnInit(): void {
    this.display$ = this.modalService.watch();
    this.foundValidation$ = this.validationService.getValidationRunById(this.isThereValidation.val_id)
      .pipe(
        catchError(() => {
          this.modalService.close();
          this.startValidation.emit(true);
          return EMPTY;
        })
      );
  }
  close(): void{
    this.modalService.close();
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
