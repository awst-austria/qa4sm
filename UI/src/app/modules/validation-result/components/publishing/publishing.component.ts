import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';

@Component({
  selector: 'qa-publishing',
  templateUrl: './publishing.component.html',
  styleUrls: ['./publishing.component.scss']
})
export class PublishingComponent implements OnInit {
  display$: Observable<'open' | 'close'>;
  constructor(
    private modalService: ModalWindowService
  ) { }

  ngOnInit(): void {
    this.display$ = this.modalService.watch();
  }
  close(): void{
    this.modalService.close();
  }
}
