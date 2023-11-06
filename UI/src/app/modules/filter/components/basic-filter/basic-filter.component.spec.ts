import {ComponentFixture, TestBed} from '@angular/core/testing';

import {BasicFilterComponent} from './basic-filter.component';

describe('BasicFilterComponent', () => {
  let component: BasicFilterComponent;
  let fixture: ComponentFixture<BasicFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BasicFilterComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicFilterComponent);
    component = fixture.componentInstance;
    // @ts-ignore
    component.filterModel = {
      filterDto: {
        id: 1,
        name: 'FIL_ALL_VALID_RANGE',
        description: 'Variable in valid geophysical range',
        help_text: 'Compared variable is checked for NaNs and invalid values.',
        parameterised: false,
        dialog_name: null,
        default_parameter: null,
        to_include: null,
        to_exclude: null,
        default_set_active: true,
        readonly: true,
      },
      enabled: true,
      readonly: false,
      parameters$: null
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
