import {ComponentFixture, TestBed} from '@angular/core/testing';

import {LoginComponent} from './login.component';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  const loginServiceSpy = jasmine.createSpyObj('AuthService', ['login']);
  const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
  const toastServiceSpy = jasmine.createSpyObj('ToastService', ['showSuccessWithHeader', 'showErrorWithHeader']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LoginComponent ],
      providers: [
        {provide: AuthService, useValue: loginServiceSpy},
        {provide: Router, useValue: routerSpy},
        {provide: ToastService, useValue: toastServiceSpy}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
