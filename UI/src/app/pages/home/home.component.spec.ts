import {ComponentFixture, TestBed} from '@angular/core/testing';

import {HomeComponent} from './home.component';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {SettingsDto} from '../../modules/core/services/global/settings.dto';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;

  // let settingsService: SettingsService;
  // let settingsServiceStub: Partial<SettingsService>;
  let getAllSettingsSpy: jasmine.Spy;
  let fakeSettings: SettingsDto;

  beforeEach(async () => {
    const settingsService = jasmine.createSpyObj('SettingsService', ['getAllSettings']);
    fakeSettings = {
      id: 1,
      maintenance_mode: false,
      news: 'some news',
    };


    getAllSettingsSpy = settingsService.getAllSettings.and.returnValue(fakeSettings);

    await TestBed.configureTestingModule({
      declarations: [HomeComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
