import {TestBed} from '@angular/core/testing';

import {AuthGuard} from './auth.guard';
import {AuthService} from './modules/core/services/auth/auth.service';
import {Router} from '@angular/router';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  const authServiceSpy = jasmine.createSpyObj('AuthService', ['isAuthenticated']);
  const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        {provide: AuthService, useValue: authServiceSpy},
        {provide: Router, useValue: routerSpy}
      ]
    });
    guard = TestBed.inject(AuthGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
