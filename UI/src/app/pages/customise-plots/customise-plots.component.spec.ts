import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomisePlotsComponent } from './customise-plots.component';

describe('CustomisePlotsComponent', () => {
  let component: CustomisePlotsComponent;
  let fixture: ComponentFixture<CustomisePlotsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomisePlotsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomisePlotsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
