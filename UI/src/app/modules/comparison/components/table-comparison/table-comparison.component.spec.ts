import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableComparisonComponent } from './table-comparison.component';

describe('TableComparisonComponent', () => {
  let component: TableComparisonComponent;
  let fixture: ComponentFixture<TableComparisonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TableComparisonComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TableComparisonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
