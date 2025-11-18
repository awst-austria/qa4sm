import {Component, EventEmitter, Input, OnInit, Output, signal} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {FormBuilder, Validators} from '@angular/forms';
import {PublishingForm} from '../../../core/services/form-interfaces/publishing-form';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';

@Component({
    selector: 'qa-publishing',
    templateUrl: './publishing.component.html',
    styleUrls: ['./publishing.component.scss'],
    standalone: false
})
export class PublishingComponent implements OnInit {
  formErrors: any;
  @Input() validationId: string;
  @Output() openPublishWindow = new EventEmitter();
  @Output() startPublishing = new EventEmitter();

  publishingForm = this.formBuilder.group<PublishingForm>({
    title: ['', [Validators.required]],
    description: ['', [Validators.required]],
    keywords: ['', [Validators.required]],
    name: ['', [Validators.required]],
    affiliation: [''],
    orcid: ['', [Validators.maxLength(25)]]
  });

  publishResultsObserver = {
    next: () => this.onPublishResultNext(),
    error: (error: CustomHttpError) => this.onPublishResultError(error)
  }

  metadataFetchError = signal(false);


  // todo: this error handling will be added after restructuring the code that calls this feature
  getPublishingFormDataObserver = {
    next: (data: any) => this.onGetPublishingFormDataNext(data),
    error: () => this.onFetchMetdataError()
  }

  onFetchMetdataError(): void{
    this.publishingForm.controls.keywords.setValue('soil moisture, validation, qa4sm')
    this.metadataFetchError.set(true);
  }

  constructor(
    private validationrunService: ValidationrunService,
    private formBuilder: FormBuilder,
    private toastService: ToastService
  ) {
  }

  ngOnInit(): void {
    this.getPublishingForm();
  }

  handleModalWindow(open): void {
    this.openPublishWindow.emit(open)
  }

  publish(): void {
    this.formErrors = [];
    this.validationrunService.publishResults(this.validationId, this.publishingForm.value)
      .subscribe(this.publishResultsObserver);
  }

  private onPublishResultNext(): void {
    this.startPublishing.emit(true)
    this.handleModalWindow(false);
  }

  private onPublishResultError(error: CustomHttpError): void {
    if (error.form) {
      this.formErrors = error.form;
      this.toastService.showErrorWithHeader('Invalid metadata',
        'Provided metadata is invalid. Please fix the errors and submit form one more time.')
    } else {
      this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
    }
    this.handleModalWindow(true);
  }

  getPublishingForm(): void {
    const params = new HttpParams().set('id', this.validationId);
    this.validationrunService.getPublishingFormData(params)
      .subscribe(this.getPublishingFormDataObserver);
  }

  private onGetPublishingFormDataNext(data): void{
    this.publishingForm.patchValue(data);
  }

}
