import {TestBed} from '@angular/core/testing';

import {ModalWindowService} from './modal-window.service';

describe('ModalWindowService', () => {
  let service: ModalWindowService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ModalWindowService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
