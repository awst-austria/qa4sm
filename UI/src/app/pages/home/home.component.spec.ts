import {ComponentFixture, TestBed} from '@angular/core/testing';

import {HomeComponent} from './home.component';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {SettingsDto} from '../../modules/core/services/global/settings.dto';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {BehaviorSubject} from 'rxjs';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let getAllSettingsSpy: jasmine.Spy;
  let fakeSettings: SettingsDto;
  let fakeIsAuthenticated$: BehaviorSubject<any>;

  beforeEach(async () => {
    const settingsServiceSpy = jasmine.createSpyObj('SettingsService', ['getAllSettings']);
    const galleryServiceSpy = jasmine.createSpyObj('Gallery', ['load']);
    fakeIsAuthenticated$ = new BehaviorSubject<boolean>(false);
    const fakeAuthService: Pick<AuthService, 'authenticated$'> = {
      authenticated$: fakeIsAuthenticated$
    };

    getAllSettingsSpy = settingsServiceSpy.getAllSettings.and.returnValue(fakeSettings);
    fakeSettings = {
      id: 1,
      maintenance_mode: false,
      news: 'some news',
      sum_link: 'link',
      feed_link: 'link'
    };

    await TestBed.configureTestingModule({
      declarations: [HomeComponent],
      providers: [
        {provide: SettingsService, useValue: settingsServiceSpy},
        {provide: AuthService, useValue: fakeAuthService}]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });


  it('should create',  () => {
    expect(component).toBeTruthy();
  });

});
