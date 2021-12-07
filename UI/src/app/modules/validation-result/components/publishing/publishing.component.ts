import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {FormBuilder, Validators} from '@angular/forms';

@Component({
  selector: 'qa-publishing',
  templateUrl: './publishing.component.html',
  styleUrls: ['./publishing.component.scss']
})
export class PublishingComponent implements OnInit {
  formErrors: any;
  display$: Observable<'open' | 'close'>;
  publishingInProgress = false;
  @Input() validationId: string;

  publishingForm = this.formBuilder.group({
    title: ['', [Validators.required]],
    description: ['', [Validators.required]],
    keywords: ['', [Validators.required]],
    name: ['', [Validators.required]],
    affiliation: [''],
    orcid: ['', [Validators.maxLength(25)]]
  });

  constructor(
    private modalService: ModalWindowService,
    private validationrunService: ValidationrunService,
    private formBuilder: FormBuilder,
  ) { }

  ngOnInit(): void {
    this.display$ = this.modalService.watch();
    this.getPublishingForm();
  }
  close(): void{
    this.modalService.close();
  }
  publish(): void{
    // this.publishingInProgress = true;
    this.validationrunService.changePublishingStatus(true);
    this.close();
    this.validationrunService.publishResults(this.validationId, this.publishingForm.value).subscribe(
      () => {
        this.validationrunService.changePublishingStatus(false);
        window.location.reload();
      },
      error => {
        // refreshing the window so that error messages shows up
        this.modalService.open();
        this.formErrors = error.error;
      });
  }
  getPublishingForm(): void{
    const params = new HttpParams().set('id', this.validationId);
    this.validationrunService.getPublishingFormData(params).subscribe(data => {
      this.publishingForm.controls.title.setValue(data.title);
      this.publishingForm.controls.description.setValue(data.description);
      this.publishingForm.controls.keywords.setValue(data.keywords);
      this.publishingForm.controls.name.setValue(data.name);
      this.publishingForm.controls.affiliation.setValue(data.affiliation);
      this.publishingForm.controls.orcid.setValue(data.orcid);
    },
    error => {},
      () =>
      //  here I refresh the window, so the submit button is not disabled
      {this.modalService.open();
      });
  }
}
