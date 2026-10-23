import {ComponentFixture, TestBed} from '@angular/core/testing';
import {BehaviorSubject} from 'rxjs';
import {providePrimeNG} from 'primeng/config';

import {FilterModule} from '../../filter.module';
import {FilterModel} from '../basic-filter/filter-model';
import {FilterDto} from '../../../core/services/filter/filter.dto';
import {IsmnDepthSettingsComponent} from './ismn-depth-settings.component';

function filterModel(parameters: string): FilterModel {
  const dto = new FilterDto(0, '', '', '', true, '', parameters, '', '', false, false);
  return new FilterModel(dto, false, false, new BehaviorSubject<string>(parameters));
}

describe('IsmnDepthSettingsComponent', () => {
  let fixture: ComponentFixture<IsmnDepthSettingsComponent>;
  let component: IsmnDepthSettingsComponent;
  let tolerances: FilterModel;

  async function setUp(depthParameters: string, toleranceParameters = '0.10,0.10'): Promise<void> {
    tolerances = filterModel(toleranceParameters);
    fixture = TestBed.createComponent(IsmnDepthSettingsComponent);
    component = fixture.componentInstance;
    component.depthFilterModel$ = new BehaviorSubject(filterModel(depthParameters));
    component.tolerancesFilterModel$ = new BehaviorSubject(tolerances);
    await render();
  }

  // The tests change state by calling the component directly, not through
  // an event, which is what would otherwise mark the view for checking. And
  // ngModel hands values to the widgets asynchronously, so let that settle
  // (along with the 400 ms commit debounce) before looking at the inputs.
  async function render(): Promise<void> {
    fixture.componentRef.changeDetectorRef.markForCheck();
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.componentRef.changeDetectorRef.markForCheck();
    fixture.detectChanges();
  }

  async function mergeOn(): Promise<void> {
    component.toggleMergeStations(true);
    await render();
  }

  function field(id: string): HTMLInputElement {
    return fixture.nativeElement.querySelector(`#${id}`);
  }

  // press and release one of the widget's own spinner buttons
  async function spin(id: string, direction: 'up' | 'down'): Promise<void> {
    const widget = field(id).closest('p-inputnumber');
    const button = widget.querySelector(direction === 'up'
      ? '.p-inputnumber-increment-button' : '.p-inputnumber-decrement-button');
    button.dispatchEvent(new MouseEvent('mousedown', {button: 0, bubbles: true}));
    button.dispatchEvent(new MouseEvent('mouseup', {button: 0, bubbles: true}));
    await render();
  }

  function warnings(): string {
    return Array.from(fixture.nativeElement.querySelectorAll('.depth-warning'))
      .map((el: Element) => el.textContent.trim().replace(/\s+/g, ' '))
      .join(' | ');
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterModule],
      providers: [providePrimeNG()],
    }).compileComponents();
  });

  it('splits the depth range evenly when merging is switched on', async () => {
    await setUp('0.10,0.20');
    await mergeOn();

    expect(component.topTolerance).toBe(0.05);
    expect(component.bottomTolerance).toBe(0.05);
    expect(tolerances.parameters$.value).toBe('0.05,0.05');
    expect(component.topBandLabel()).toBe('0.05–0.15 m');
    expect(component.bottomBandLabel()).toBe('0.15–0.25 m');
    expect(field('ismn_top_tolerance').value).toBe('0.05 m');
    expect(field('ismn_bottom_tolerance').value).toBe('0.05 m');
    expect(warnings()).toBe('');
  });

  it('rounds the even split down', async () => {
    await setUp('0.00,0.15');
    await mergeOn();
    expect(component.topTolerance).toBe(0.07);
    expect(component.bottomTolerance).toBe(0.07);

    component.toggleMergeStations(false);
    component.depthFrom = 0.03;
    component.depthTo = 0.08;
    await mergeOn();
    expect(component.topTolerance).toBe(0.02);
    expect(component.bottomTolerance).toBe(0.02);
  });

  it('keeps the top band from reaching above the surface', async () => {
    await setUp('0.00,0.10');
    await mergeOn();
    expect(component.topBandLabel()).toBe('0–0.05 m');
    expect(component.bottomBandLabel()).toBe('0.05–0.15 m');
  });

  it('holds a spinner at the limit and warns instead of overlapping', async () => {
    await setUp('0.10,0.20');
    await mergeOn();

    await spin('ismn_bottom_tolerance', 'up');
    expect(component.bottomTolerance).toBe(0.05);
    expect(field('ismn_bottom_tolerance').value).toBe('0.05 m');
    expect(warnings()).toContain('Bottom tolerance can be at most 0.05 m');

    await spin('ismn_top_tolerance', 'up');
    expect(component.topTolerance).toBe(0.05);
    expect(field('ismn_top_tolerance').value).toBe('0.05 m');
    expect(warnings()).toContain('Top tolerance can be at most 0.05 m');

    component.onTolerancesBlur();
    expect(tolerances.parameters$.value).toBe('0.05,0.05');
  });

  it('gives one tolerance the room the other one frees', async () => {
    await setUp('0.10,0.20');
    await mergeOn();

    await spin('ismn_top_tolerance', 'down');
    expect(component.topTolerance).toBe(0.04);
    expect(warnings()).toBe('');

    await spin('ismn_bottom_tolerance', 'up');
    expect(Math.round(component.bottomTolerance * 100)).toBe(6);
    expect(warnings()).toBe('');

    await spin('ismn_bottom_tolerance', 'up');
    expect(Math.round(component.bottomTolerance * 100)).toBe(6);
    expect(field('ismn_bottom_tolerance').value).toBe('0.06 m');
    expect(warnings()).toContain('Bottom tolerance can be at most 0.06 m');

    component.onTolerancesBlur();
    expect(tolerances.parameters$.value).toBe('0.04,0.06');
    expect(component.topBandLabel()).toBe('0.06–0.14 m');
    expect(component.bottomBandLabel()).toBe('0.14–0.26 m');
  });

  it('holds a typed value at the limit', async () => {
    await setUp('0.10,0.20');
    await mergeOn();

    component.onTopToleranceEdited(0.3);
    await render();
    expect(component.topTolerance).toBe(0.05);
    expect(field('ismn_top_tolerance').value).toBe('0.05 m');
    expect(warnings()).toContain('Top tolerance can be at most 0.05 m');

    component.onTopToleranceEdited(0.03);
    await render();
    expect(component.topTolerance).toBe(0.03);
    expect(warnings()).toBe('');
  });

  it('shrinks both tolerances in proportion when the range narrows', async () => {
    await setUp('0.10,0.20');
    await mergeOn();
    component.onTopToleranceEdited(0.02);
    component.onBottomToleranceEdited(0.08);

    component.depthTo = 0.18;
    component.onDepthEdited();
    component.onDepthBlur();
    await render();

    // 0.02 and 0.08 scaled by 0.08 / 0.10, each rounded down
    expect(component.topTolerance).toBe(0.01);
    expect(component.bottomTolerance).toBe(0.06);
    expect(tolerances.parameters$.value).toBe('0.01,0.06');
    expect(field('ismn_bottom_tolerance').value).toBe('0.06 m');
    expect(warnings()).toContain('too narrow');
  });

  it('leaves the tolerances alone while the range is empty or inverted', async () => {
    await setUp('0.10,0.20');
    await mergeOn();

    component.depthTo = 0.1;
    component.onDepthEdited();
    component.onDepthBlur();
    await render();
    expect(component.topTolerance).toBe(0.05);
    expect(component.bottomTolerance).toBe(0.05);
    expect(warnings()).toContain('bands overlap');

    component.depthTo = 0.05;
    component.onDepthEdited();
    component.onDepthBlur();
    await render();
    expect(component.topTolerance).toBe(0.05);
    expect(warnings()).toContain('inverted');
    expect(warnings()).not.toContain('bands overlap');
  });

  it('flags overlapping bands that a saved validation brings back', async () => {
    // the old default: 0.1 m each on a 0-0.1 m range
    await setUp('0.00,0.10', '0.10,0.10');
    tolerances.enabled = true;
    await render();
    expect(component.bandsOverlap()).toBeTrue();
    expect(warnings()).toContain('bands overlap');

    // the bottom band already takes the whole range, so the top tolerance
    // comes straight down to the only value that fits
    await spin('ismn_top_tolerance', 'down');
    expect(component.topTolerance).toBe(0);
    expect(component.bandsOverlap()).toBeFalse();
    expect(warnings()).not.toContain('bands overlap');
  });
});
