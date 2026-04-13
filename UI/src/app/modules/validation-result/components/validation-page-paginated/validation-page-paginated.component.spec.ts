import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ValidationPagePaginatedComponent} from './validation-page-paginated.component';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {of} from 'rxjs';

describe('ValidationPagePaginatedComponent', () => {
  let component: ValidationPagePaginatedComponent;
  let fixture: ComponentFixture<ValidationPagePaginatedComponent>;


  beforeEach(async () => {
    const validationrunServiceSpy = jasmine.createSpyObj('ValidationrunService',
      [
        'getMyValidationruns',
        'getPublishedValidationruns',
        'getValidationRunById',
        'getMyValidationruns'],
      {
        doRefresh: of(false)
      },
 );

    await TestBed.configureTestingModule({
      imports : [
      ],
      declarations: [ValidationPagePaginatedComponent],
      providers: [{provide: ValidationrunService, useValue: validationrunServiceSpy}]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ValidationPagePaginatedComponent);
    component = fixture.componentInstance;
    component.published = false;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
