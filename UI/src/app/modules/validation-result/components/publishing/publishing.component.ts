import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {PublishingFormDto} from '../../../core/services/validation-run/publishing-form.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';

@Component({
  selector: 'qa-publishing',
  templateUrl: './publishing.component.html',
  styleUrls: ['./publishing.component.scss']
})
export class PublishingComponent implements OnInit {
  publishingForm$: Observable<PublishingFormDto>;
  display$: Observable<'open' | 'close'>;
  @Input() validationId: string;

  constructor(
    private modalService: ModalWindowService,
    private validationrunService: ValidationrunService
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
    console.log('Monika');
  }
  getPublishingForm(): void{
    const params = new HttpParams().set('id', this.validationId);
    this.publishingForm$ = this.validationrunService.getPublishingFormData(params);
  }
}
