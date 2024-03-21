import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {HttpParams} from '@angular/common/http';
import {Router} from '@angular/router';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {BehaviorSubject, Observable, Observer} from 'rxjs';
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
  isTrackedByTheUser$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  status: string;
  publishingInProgress$: Observable<boolean>;
  isArchived$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(null);


  constructor(private router: Router,
              private validationService: ValidationrunService,
              public authService: AuthService,
              public globals: GlobalParamsService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.isLogged = this.authService.currentUser.id != null;
    this.isOwner = this.authService.currentUser.id === this.validationRun.user;
    this.isTrackedByTheUser$.next(this.authService.currentUser.copied_runs.includes(this.validationRun.id));
    this.isArchived$.next(this.validationRun.is_archived);
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

  // next, errors, complete functions
  onDeleteNext(): void {
    this.validationService.refreshComponent('page');
    this.doUpdate.emit({key: 'delete', value: true});
  }

  onArchiveNext(resp, validationId, archive): void {
    this.validationService.refreshComponent(validationId);
    this.isArchived$.next(archive);
    this.doUpdate.emit({key: 'archived', value: resp.body});
  }

  onExtendResultsNext(resp, validationId): void {
    this.validationService.refreshComponent(validationId);
    this.doUpdate.emit({key: 'extended', value: resp.body});
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
    this.validationService.addValidation(validationId).subscribe(
      response => {
        // re-initi auth service to update user data - to update list of added runs
        this.authService.init();
        this.isTrackedByTheUser$.next(true);
        // this one is needed to refresh tracked-validations component
        this.doRefresh.emit(true);
        alert(response);


      });
    this.authService.init();
  }

  removeValidation(validationId: string): void {
    if (!confirm('Do you really want to remove this validation from your list?')) {
      return;
    }
    this.validationService.removeValidation(validationId).subscribe(
      response => {
        // re-initi auth service to update user data - to update list of added runs
        this.authService.init();
        this.isTrackedByTheUser$.next(false);
        // this one is needed to refresh tracked-validations component
        this.doRefresh.emit(true);
        alert(response);
      });
    this.authService.init();
  }

  open(): void {
    this.openPublishWindow.emit(true)
  }

  copy(validationId: string): void {
    let newId: string;
    const params = new HttpParams().set('validation_id', validationId);
    this.validationService.copyValidation(params).subscribe(data => {
      newId = data.run_id;
      alert('This validation will be copied and add to the list of your validations.');
      this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
        this.router.navigate([`validation-result/${newId}`]);
      });
    });
  }
}
