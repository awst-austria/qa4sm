import {ComponentFixture, TestBed} from '@angular/core/testing';

import {DatasetReferenceComponent} from './dataset-reference.component';

describe('DatasetReferenceComponent', () => {
  let component: DatasetReferenceComponent;
  let fixture: ComponentFixture<DatasetReferenceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DatasetReferenceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DatasetReferenceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
