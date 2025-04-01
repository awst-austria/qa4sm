import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FilteringFormComponent } from './filtering-form.component';

describe('FilteringFormComponent', () => {
  let component: FilteringFormComponent;
  let fixture: ComponentFixture<FilteringFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilteringFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FilteringFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
