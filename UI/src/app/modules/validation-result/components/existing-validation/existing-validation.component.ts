import {Component, OnInit} from '@angular/core';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';
import {Observable} from 'rxjs';

@Component({
  selector: 'qa-existing-validation',
  templateUrl: './existing-validation.component.html',
  styleUrls: ['./existing-validation.component.scss']
})
export class ExistingValidationComponent implements OnInit {
  display$: Observable<'open' | 'close'>;

  constructor(private modalService: ModalWindowService) { }

  ngOnInit(): void {
    this.display$ = this.modalService.watch();
  }
  close(): void{
    this.modalService.close();
  }

}
