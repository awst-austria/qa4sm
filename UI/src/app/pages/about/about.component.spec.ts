import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {AboutComponent} from './about.component';
import {GlobalParamsService} from '../../modules/core/services/global/global-params.service';

describe('AboutComponent', () => {
  let component: AboutComponent;
  let fixture: ComponentFixture<AboutComponent>;
  let globalParamServiceStub: Partial<GlobalParamsService>;
  let globalService: GlobalParamsService;

  beforeEach(async () => {
    globalParamServiceStub = {
      globalContext: {
        admin_mail: '',
        doi_prefix: '',
        site_url: '',
        app_version: '1.6.0',
        expiry_period: '',
        warning_period: '',
      }
    };
    await TestBed.configureTestingModule({
      declarations: [ AboutComponent ],
      providers: [{provide: GlobalParamsService, useValue: globalParamServiceStub}]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AboutComponent);
    component = fixture.componentInstance;
    globalService = fixture.debugElement.injector.get(GlobalParamsService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get appropriate app version number', () => {
    expect(component.getAppVersion()).toEqual('1.6.0');
  });

  it('should render the logo', async(() => {
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('div#introduction>a>img').src).toContain('/images/logo/logo_ffg.png');
    expect(compiled.querySelector('table.table>tbody>:first-child>td>a>img').src).toContain('/images/logo/logo_tuwien_geo.png');
    expect(compiled.querySelector('table.table>tbody>:nth-child(2)>td>a>img').src).toContain('/images/logo/logo_awst.png');
  }));

});
