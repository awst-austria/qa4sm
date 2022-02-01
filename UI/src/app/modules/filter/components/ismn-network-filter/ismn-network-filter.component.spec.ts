import {ComponentFixture, TestBed} from '@angular/core/testing';

import {IsmnNetworkFilterComponent} from './ismn-network-filter.component';

describe('IsmnNetworkFilterComponent', () => {
  let component: IsmnNetworkFilterComponent;
  let fixture: ComponentFixture<IsmnNetworkFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [IsmnNetworkFilterComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IsmnNetworkFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
