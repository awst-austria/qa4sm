import {TestBed} from '@angular/core/testing';

import {ToastService} from './toast.service';
import {MessageService} from 'primeng/api';

describe('ToastService', () => {
  let service: ToastService;
  let messageService: MessageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ToastService);
    messageService = TestBed.inject(MessageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
