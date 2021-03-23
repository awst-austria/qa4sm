import {ComponentFixture, TestBed} from '@angular/core/testing';

import {SortingFormComponent} from './sorting-form.component';

describe('SortingFormComponent', () => {
  let component: SortingFormComponent;
  let fixture: ComponentFixture<SortingFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SortingFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SortingFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
