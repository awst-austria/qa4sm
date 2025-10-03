import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JsonConfigComponent } from './json-config.component';

describe('JsonConfigComponent', () => {
  let component: JsonConfigComponent;
  let fixture: ComponentFixture<JsonConfigComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JsonConfigComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JsonConfigComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
