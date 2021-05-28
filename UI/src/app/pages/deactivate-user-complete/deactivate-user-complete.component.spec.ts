import {ComponentFixture, TestBed} from '@angular/core/testing';

import {DeactivateUserCompleteComponent} from './deactivate-user-complete.component';

describe('DeactivateUserCompleteComponent', () => {
  let component: DeactivateUserCompleteComponent;
  let fixture: ComponentFixture<DeactivateUserCompleteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeactivateUserCompleteComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeactivateUserCompleteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
