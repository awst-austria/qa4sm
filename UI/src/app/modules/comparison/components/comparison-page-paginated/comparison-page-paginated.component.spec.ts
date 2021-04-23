import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComparisonPagePaginatedComponent } from './comparison-page-paginated.component';

describe('ComparisonPagePaginatedComponent', () => {
  let component: ComparisonPagePaginatedComponent;
  let fixture: ComponentFixture<ComparisonPagePaginatedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ComparisonPagePaginatedComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ComparisonPagePaginatedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
