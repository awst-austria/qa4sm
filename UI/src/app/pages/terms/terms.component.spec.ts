import {ComponentFixture, TestBed} from '@angular/core/testing';

import {TermsComponent} from './terms.component';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';

describe('TermsComponent', () => {
  let component: TermsComponent;
  let fixture: ComponentFixture<TermsComponent>;
  let globalParamServiceStub: Partial<GlobalParamsService>;
  let globalService: GlobalParamsService;

  beforeEach(async () => {
    globalParamServiceStub = {
      globalContext: {
        admin_mail: 'admin@qa4sm.eu',
        doi_prefix: '',
        site_url: 'qa4sm.eu',
        app_version: '1.6.0',
        expiry_period: '',
        warning_period: '',
      }
    };
    await TestBed.configureTestingModule({
      declarations: [ TermsComponent ],
      providers: [{provide: GlobalParamsService, useValue: globalParamServiceStub}]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TermsComponent);
    component = fixture.componentInstance;
    globalService = fixture.debugElement.injector.get(GlobalParamsService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get appropriate email', () => {
    expect(component.getAdminMail()).toBe('admin@qa4sm.eu');
  });

  it('should get appropriate site url', () => {
    expect(component.getSiteURL()).toBe('qa4sm.eu');
  });

});
