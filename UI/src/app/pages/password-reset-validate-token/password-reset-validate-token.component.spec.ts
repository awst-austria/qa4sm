import {ComponentFixture, TestBed} from '@angular/core/testing';

import {PasswordResetValidateTokenComponent} from './password-reset-validate-token.component';

describe('PasswordResetValidateTokenComponent', () => {
  let component: PasswordResetValidateTokenComponent;
  let fixture: ComponentFixture<PasswordResetValidateTokenComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PasswordResetValidateTokenComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PasswordResetValidateTokenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
