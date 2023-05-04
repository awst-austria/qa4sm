import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserProfileComponent} from './user-profile.component';
import {AuthService} from '../../modules/core/services/auth/auth.service';

describe('UserProfileComponent', () => {
  let component: UserProfileComponent;
  let fixture: ComponentFixture<UserProfileComponent>;
  let authServiceStub: Partial<AuthService>;
  let authService: AuthService;

  beforeEach(async () => {
    authServiceStub  = {
      currentUser: {
        username: 'testUser',
        first_name: 'Jane',
        id: null,
        copied_runs: [],
        email: 'janeDoe@someDomain.at',
        last_name: 'Doe',
        organisation: '',
        country: '',
        orcid: '',
        space_left: null,
        space_limit_value: null,
        space_limit: null
      }
    };

    await TestBed.configureTestingModule({
      declarations: [ UserProfileComponent ],
      providers: [{provide: AuthService, useValue: authServiceStub}]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserProfileComponent);
    component = fixture.componentInstance;
    authService = fixture.debugElement.injector.get(AuthService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
