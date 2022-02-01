import {ComponentFixture, TestBed} from '@angular/core/testing';

import {UserFormComponent} from './user-form.component';
import {LocalApiService} from '../../core/services/auth/local-api.service';
import {AuthService} from '../../core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ReactiveFormsModule} from '@angular/forms';

describe('UserFormComponent', () => {
  let component: UserFormComponent;
  let fixture: ComponentFixture<UserFormComponent>;

  beforeEach(async () => {
    const userFormServiceSpy = jasmine.createSpyObj('LocalApiService', ['getCountryList']);
    const userServiceSpy = jasmine.createSpyObj('AuthService',
      ['signUp'],
      {
        currentUser: {
          username: '',
          first_name: '',
          id: null,
          copied_runs: [],
          email: '',
          last_name: '',
          organisation: '',
          country: '',
          orcid: ''
        }
      });
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule],
      declarations: [ UserFormComponent ],
      providers: [
        {provide: LocalApiService, useValue: userFormServiceSpy},
        {provide: AuthService, useValue: userServiceSpy},
        {provide: Router, useValue: routerSpy}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UserFormComponent);
    component = fixture.componentInstance;
    component.userData = {
      username: '',
      first_name: '',
      id: null,
      copied_runs: [],
      email: '',
      last_name: '',
      organisation: '',
      country: '',
      orcid: ''
    };
    component.selectedCountry = {
      code: '',
      name: ''
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
