import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {HttpParams} from '@angular/common/http';
import {Router} from '@angular/router';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {Observable} from 'rxjs';


@Component({
  selector: 'qa-buttons',
  templateUrl: './buttons.component.html',
  styleUrls: ['./buttons.component.scss']
})

export class ButtonsComponent implements OnInit {

  @Input() validationRun: ValidationrunDto;
  @Input() published: boolean;
  @Input() validationList: boolean;
  @Input() tracked: boolean;
  @Output() doRefresh = new EventEmitter();

  faIcons = {faArchive: fas.faArchive,
    faStop: fas.faStop,
    faFileDownload: fas.faFileDownload};

  isLogged: boolean;
  isOwner: boolean;
  isTrackedByTheUser: boolean;
  status: string;
  publishingInProgress$: Observable<boolean>;


  constructor(private router: Router,
              private validationService: ValidationrunService,
              public authService: AuthService,
              private modalService: ModalWindowService ) { }

  ngOnInit(): void {
    this.isLogged = this.authService.currentUser.id != null;
    this.isOwner = this.authService.currentUser.id === this.validationRun.user;
    this.isTrackedByTheUser = this.authService.currentUser.copied_runs.includes(this.validationRun.id);
    this.publishingInProgress$ = this.validationService.checkPublishingInProgress();
  }


  deleteValidation(validationId: string): void{
    if (!confirm('Do you really want to delete the result?')) {
      return;
    }
    this.validationService.deleteValidation(validationId).subscribe(
      () => {
        this.validationService.refreshComponent('page');
        this.doRefresh.emit(false);
      });

  }

  stopValidation(validationId: string): void{
    if (!confirm('Do you really want to stop the validation?')) {
      return;
    }
    this.validationService.stopValidation(validationId).subscribe(
      () => {
        this.validationService.refreshComponent(validationId);
      });
  }

  archiveResults(validationId: string, archive: boolean): void{
    if (!confirm('Do you want to ' + (archive ? 'archive' : 'un-archive')
      + ' the result' + (archive ? '' : ' (allow auto-cleanup)') + '?')) {
      return;
    }
    this.validationService.archiveResult(validationId, archive).subscribe(() => {
      this.validationService.refreshComponent(validationId);
      this.doRefresh.emit(true);
    });
  }

  extendResults(validationId: string): void{
    if (!confirm('Do you want to extend the lifespan of this result?')) {
      return;
    }
    this.validationService.extendResult(validationId).subscribe(() => {
      this.validationService.refreshComponent(validationId);
      this.doRefresh.emit(true);
    });
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void{
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

  addValidation(validationId: string): void{
    this.validationService.addValidation(validationId).subscribe(
        response => {
          this.validationService.refreshComponent(validationId);
          this.doRefresh.emit(true);
          alert(response);
        });
    this.authService.init();
  }

  removeValidation(validationId: string): void{
    if (!confirm('Do you really want to remove this validation from your list?')) {
      return;
    }
    this.validationService.removeValidation(validationId).subscribe(
      response => {
        this.validationService.refreshComponent(validationId);
        this.doRefresh.emit(true);
        alert(response);
      });
    this.authService.init();
  }

  open(): void{
    this.modalService.open();
  }

  copy(validationId: string): void{
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
