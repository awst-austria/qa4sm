import {Component, EventEmitter, Input, OnInit, Output, signal} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {HttpParams} from '@angular/common/http';
import {Router} from '@angular/router';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Observable, Observer} from 'rxjs';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {CustomHttpError} from '../../../core/services/global/http-error.service';

@Component({
  selector: 'qa-buttons',
  templateUrl: './buttons.component.html',
  styleUrls: ['./buttons.component.scss']
})

export class ButtonsComponent implements OnInit {

  @Input() validationRun: ValidationrunDto;
  @Input() published: boolean;
  @Input() validationList: boolean;
  @Input() canBeRerun: boolean;
  @Input() tracked: boolean;
  @Output() doRefresh = new EventEmitter();
  @Output() doUpdate = new EventEmitter();
  @Output() openPublishWindow = new EventEmitter();

  faIcons = {
    faArchive: fas.faArchive,
    faStop: fas.faStop,
    faFileDownload: fas.faFileDownload
  };

  isLogged: boolean;
  isOwner: boolean;
  isTrackedByTheUser = signal(false);
  status: string;
  publishingInProgress$: Observable<boolean>;
  isArchived = signal(undefined)

  constructor(private router: Router,
              private validationService: ValidationrunService,
              public authService: AuthService,
              public globals: GlobalParamsService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.isLogged = this.authService.currentUser.id != null;
    this.isOwner = this.authService.currentUser.id === this.validationRun.user;
    this.isTrackedByTheUser.set(this.authService.currentUser.copied_runs.includes(this.validationRun.id));
    this.isArchived.set(this.validationRun.is_archived);
  }

  // OBSERVERS

  deleteObserver = {
    next: () => this.onDeleteNext(),
    error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
    complete: () => this.toastService.showSuccess('Validation successfully removed.')
  }

  stopValidationObserver = {
    next: (validationId: string) => this.validationService.refreshComponent(validationId),
    error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
  }

  archiveObserver(validationId: string, archive: boolean): Observer<any> {
    return {
      next: (resp: any) => this.onArchiveNext(resp, validationId, archive),
      error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
      complete: () => this.toastService.showSuccess(`Results ${archive ? 'archived' : 'un-archived'} successfully.`)
    }
  }

  extendResultObserver(validationId: string): Observer<any> {
    return {
      next: (resp) => this.onExtendResultsNext(resp, validationId),
      error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
      complete: () => this.toastService.showSuccess('Results extended successfully')
    }
  }

  addValidationObserver = {
    next: (response: any) => this.onAddValidationNext(response),
    error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
  }

  removeValidationObserver = {
    next: (response: any) => this.onRemoveValidationNext(response),
    error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
  }

  // next, errors, complete functions
  onDeleteNext(): void {
    this.validationService.refreshComponent('page');
    this.doUpdate.emit({key: 'delete', value: true});
  }

  onArchiveNext(resp: { body: any; }, validationId: string, archive: boolean): void {
    this.validationService.refreshComponent(validationId);
    this.isArchived.set(archive);
    this.doUpdate.emit({key: 'archived', value: resp.body});
  }

  onExtendResultsNext(resp: { body: any; }, validationId: string): void {
    this.validationService.refreshComponent(validationId);
    this.doUpdate.emit({key: 'extended', value: resp.body});
  }

  onAddValidationNext(response): void {
    this.isTrackedByTheUser.set(true);
    this.doRefresh.emit(true);
    this.authService.init();
    this.toastService.showSuccess(response)
  }

  onRemoveValidationNext(response): void {
    this.isTrackedByTheUser.set(false);
    this.doRefresh.emit(true);
    this.authService.init();
    this.toastService.showSuccess(response)
  }


  // button functions
  deleteValidation(validationId: string): void {
    if (!confirm('Do you really want to delete the result?')) {
      return;
    }
    this.validationService.deleteValidation(validationId).subscribe(this.deleteObserver);
  }

  stopValidation(validationId: string): void {
    if (!confirm('Do you really want to stop the validation?')) {
      return;
    }
    this.validationService.stopValidation(validationId).subscribe(this.stopValidationObserver);
  }

  archiveResults(validationId: string, archive: boolean): void {
    if (!confirm('Do you want to ' + (archive ? 'archive' : 'un-archive')
      + ' the result' + (archive ? '' : ' (allow auto-cleanup)') + '?')) {
      return;
    }

    this.validationService.archiveResult(validationId, archive).subscribe(this.archiveObserver(validationId, archive));
  }

  extendResults(validationId: string): void {
    if (!confirm('Do you want to extend the lifespan of this result?')) {
      return;
    }
    this.validationService.extendResult(validationId).subscribe(this.extendResultObserver(validationId));
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

  addValidation(validationId: string): void {
    this.validationService.addValidation(validationId).subscribe(this.addValidationObserver);
  }


  removeValidation(validationId: string): void {
    if (!confirm('Do you really want to remove this validation from your list?')) {
      return;
    }
    this.validationService.removeValidation(validationId).subscribe(this.removeValidationObserver);
  }


  open(): void {
    this.openPublishWindow.emit(true)
  }


  copyValidationObserver = {
    next: (data) => this.onCopyValidationNext(data),
    error: (error: CustomHttpError) => this.onCopyValidationError(error)
  }

  onCopyValidationNext(data): void {
    const newId = data.run_id;
    this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
      this.router.navigate([`validation-result/${newId}`])
        .then(() => this.toastService.showSuccess('Validation copied successfully'));
    });
  }

  onCopyValidationError(error: CustomHttpError): void{
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
  }

  copy(validationId: string): void {
    // let newId: string;
    alert('This validation will be copied and added to the list of your validations.');
    const params = new HttpParams().set('validation_id', validationId);
    this.validationService.copyValidation(params)
      .subscribe(this.copyValidationObserver);
  }
}
