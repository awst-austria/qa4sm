import {ComponentFixture, TestBed} from '@angular/core/testing';

import {MaintenanceModeComponent} from './maintenance-mode.component';

describe('MaintenanceModeComponent', () => {
  let component: MaintenanceModeComponent;
  let fixture: ComponentFixture<MaintenanceModeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MaintenanceModeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MaintenanceModeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
