import {ComponentFixture, TestBed} from '@angular/core/testing';

import {PasswordResetDoneComponent} from './password-reset-done.component';

describe('PasswordResetDoneComponent', () => {
  let component: PasswordResetDoneComponent;
  let fixture: ComponentFixture<PasswordResetDoneComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PasswordResetDoneComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PasswordResetDoneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
