import {ComponentFixture, TestBed} from '@angular/core/testing';

import {AnomClimatologyComponent} from './anom-climatology.component';

describe('AnomClimatologyComponent', () => {
  let component: AnomClimatologyComponent;
  let fixture: ComponentFixture<AnomClimatologyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AnomClimatologyComponent]
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AnomClimatologyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
