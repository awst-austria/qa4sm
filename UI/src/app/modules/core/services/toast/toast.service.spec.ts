import {TestBed} from '@angular/core/testing';

import {ToastService} from './toast.service';
import {MessageService} from 'primeng/api';

describe('ToastService', () => {
  let service: ToastService;

  beforeEach(() => {
    const messageServiceSpy = jasmine.createSpyObj('MessageService', ['add']);
    TestBed.configureTestingModule({
      providers: [{provide: MessageService, useValue: messageServiceSpy}]
    });
    service = TestBed.inject(ToastService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
