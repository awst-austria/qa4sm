import {ComponentFixture, TestBed} from '@angular/core/testing';

import {MyDatasetsComponent} from './my-datasets.component';

describe('MyDatasetsComponent', () => {
  let component: MyDatasetsComponent;
  let fixture: ComponentFixture<MyDatasetsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MyDatasetsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MyDatasetsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
