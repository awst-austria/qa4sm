import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ButtonsComponent} from './buttons.component';
import {Router} from '@angular/router';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';

describe('ButtonsComponent', () => {
  let component: ButtonsComponent;
  let fixture: ComponentFixture<ButtonsComponent>;

  beforeEach(async () => {
    const routerSpy = jasmine.createSpyObj('Router', ['navigateByUrl', 'navigate']);
    const validationServiceSpy = jasmine.createSpyObj('ValidationService',
      [
        'deleteValidation',
        'refreshComponent',
        'stopValidation',
        'archiveResult',
        'extendResult',
        'downloadResultFile',
        'addValidation',
        'removeValidation',
        'copyValidation'
      ]
    );
    const authServiceSpy = jasmine.createSpyObj('AuthService',
      ['init'],
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
    const modalServiceSpy = jasmine.createSpyObj('ModalWindowService', ['open']);
    await TestBed.configureTestingModule({
      declarations: [ButtonsComponent],
      providers: [
        {provide: Router, useValue: routerSpy},
        {provide: ValidationrunService, useValue: validationServiceSpy},
        {provide: AuthService, useValue: authServiceSpy},
        {provide: ModalWindowService, useValue: modalServiceSpy}
      ]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ButtonsComponent);
    component = fixture.componentInstance;
    component.validationRun = {
      temporal_reference_configuration: 1,
      dataset_configurations: [1, 2],
      scaling_reference_configuration: 1,
      temporal_matching: 12,
      bootstrap_tcol_cis: false,
      anomalies: 'none',
      anomalies_from: null,
      anomalies_to: null,
      copied_run: [],
      doi: '10030-10102/11',
      end_time: new Date('2021-10-05T12:53:27.424039Z'),
      error_points: 0,
      expiry_date: new Date('2021-12-04T12:53:27.424Z'),
      expiry_notified: false,
      id: '',
      interval_from: new Date('1978-11-01T00:00:00Z'),
      interval_to: new Date('2019-12-31T23:59:59.999999Z'),
      is_a_copy: false,
      is_archived: false,
      is_near_expiry: false,
      is_unpublished: true,
      last_extended: null,
      max_lat: 71.6,
      max_lon: 48.3,
      min_lat: 34,
      min_lon: -11.2,
      name_tag: 'second validation',
      ok_points: 0,
      output_dir_url: null,
      output_file: null,
      output_file_name: null,
      progress: 0,
      publishing_in_progress: false,
      spatial_reference_configuration: 4699,
      scaling_method: 'mean_std',
      scaling_ref: 4699,
      start_time: new Date('2021-10-05T12:53:27.156239Z'),
      tcol: false,
      total_points: 0,
      user: 1,
    };
    component.published = false;
    component.validationList = false;
    component.tracked = false;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
