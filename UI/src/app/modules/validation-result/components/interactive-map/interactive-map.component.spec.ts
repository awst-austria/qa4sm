import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InteractiveMapComponent } from './interactive-map.component';

describe('InteractiveMapComponent', () => {
  let component: InteractiveMapComponent;
  let fixture: ComponentFixture<InteractiveMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InteractiveMapComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InteractiveMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
