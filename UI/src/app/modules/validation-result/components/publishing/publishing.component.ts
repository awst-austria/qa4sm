import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {FormBuilder, Validators} from '@angular/forms';
import {Router} from '@angular/router';

@Component({
  selector: 'qa-publishing',
  templateUrl: './publishing.component.html',
  styleUrls: ['./publishing.component.scss']
})
export class PublishingComponent implements OnInit {
  formErrors: any;
  display$: Observable<'open' | 'close'>;
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
    private router: Router
  ) { }

  ngOnInit(): void {
    this.display$ = this.modalService.watch();
    this.getPublishingForm();
  }
  close(): void{
    this.modalService.close();
    // this.publishingOn.emit(false);
  }
  publish(): void{
    this.validationrunService.publishResults(this.validationId, this.publishingForm.value).subscribe(
      () => {
        this.close();
        window.location.reload();
      },
      error => {
        console.log(error.error);
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
    });
  }
}
