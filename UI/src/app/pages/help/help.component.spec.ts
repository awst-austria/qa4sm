import {ComponentFixture, TestBed} from '@angular/core/testing';

import {HelpComponent} from './help.component';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';

describe('HelpComponent', () => {
  let component: HelpComponent;
  let fixture: ComponentFixture<HelpComponent>;
  let globalParamServiceStub: Partial<GlobalParamsService>;
  let globalService: GlobalParamsService;

  beforeEach(async () => {
    globalParamServiceStub = {
      globalContext: {
        admin_mail: 'mainUser@qa4sm.eu',
        doi_prefix: '',
        site_url: '',
        app_version: '1.6.0',
        expiry_period: '7',
        warning_period: '60',
        temporal_matching_default: 0
      }
    };

    await TestBed.configureTestingModule({
      declarations: [ HelpComponent ],
      providers: [{provide: GlobalParamsService, useValue: globalParamServiceStub}]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HelpComponent);
    component = fixture.componentInstance;
    globalService = fixture.debugElement.injector.get(GlobalParamsService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get appropriate expiry period', () => {
    expect(component.getExpiryPeriod()).toBe('7');
  });

  it('should get appropriate warning period', () => {
    expect(component.getWarningPeriod()).toBe('60');
  });

  it('should get appropriate email', () => {
    expect(component.getAdminMail()).toBe('mainUser@qa4sm.eu');
  });

});
