import {ComponentFixture, TestBed} from '@angular/core/testing';

import {NavigationBarComponent} from './navigation-bar.component';
import {BehaviorSubject} from 'rxjs';
import {AuthService} from '../../../core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../../core/services/toast/toast.service';

describe('NavigationBarComponent', () => {
  let component: NavigationBarComponent;
  let fixture: ComponentFixture<NavigationBarComponent>;

  beforeEach(async () => {
    const authServiceSpy = jasmine.createSpyObj('AuthService',
      ['logout'],
      {authenticated: new BehaviorSubject(false)});
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const toastServiceSpy = jasmine.createSpyObj('ToastService', ['showSuccessWithHeader']);

    await TestBed.configureTestingModule({
      declarations: [ NavigationBarComponent ],
      providers: [
        {provide: AuthService, useValue: authServiceSpy},
        {provide: Router, useValue: routerSpy},
        {provide: ToastService, useValue: toastServiceSpy}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NavigationBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
