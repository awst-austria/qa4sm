import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationPagePaginatedComponent} from './validation-page-paginated.component';

describe('ValidationPagePaginatedComponent', () => {
  let component: ValidationPagePaginatedComponent;
  let fixture: ComponentFixture<ValidationPagePaginatedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValidationPagePaginatedComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationPagePaginatedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
