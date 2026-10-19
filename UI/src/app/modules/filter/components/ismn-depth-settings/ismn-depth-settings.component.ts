import {Component, EventEmitter, Input, OnDestroy, OnInit, Output, ViewChild} from '@angular/core';
import {InputNumber} from 'primeng/inputnumber';
import {BehaviorSubject, Subject} from 'rxjs';
import {debounceTime, takeUntil} from 'rxjs/operators';

import {FilterModel} from '../basic-filter/filter-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';

type BandEdge = 'top' | 'bottom';

/**
 * The ISMN measurement depth and, optionally, the sensor merging tolerances.
 *
 * These are two separate parametrised filters on the backend - FIL_ISMN_DEPTH
 * carries "from,to" and FIL_ISMN_TOLERANCES carries "top,bottom" and is applied
 * only while it is enabled - but they describe one decision, so they are shown
 * as one panel. Nothing about how they reach the validation changes: the same
 * two parameter strings are written to the same two filter models.
 */
@Component({
  selector: 'qa-ismn-depth-settings',
  templateUrl: './ismn-depth-settings.component.html',
  styleUrls: ['./ismn-depth-settings.component.scss'],
  standalone: false
})
export class IsmnDepthSettingsComponent implements OnInit, OnDestroy {

  @Input() depthFilterModel$: BehaviorSubject<FilterModel>;
  @Input() tolerancesFilterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;
  // set while another setting rules merging out (the validate page decides
  // which); shown as a warning, and keeps merging from being switched on,
  // though never from being switched off
  @Input() mergeBlockedReason: string | null = null;

  @Output() depthSelectionChanged = new EventEmitter<string>();
  @Output() tolerancesSelectionChanged = new EventEmitter<string>();

  depthFrom = 0;
  depthTo = 0.1;
  topTolerance = 0.1;
  bottomTolerance = 0.1;

  // why the tolerances are not what the user last asked for: an edit held at
  // the limit because the bands would have overlapped, or both tolerances cut
  // down to fit a narrower depth range. Cleared by the next edit that goes
  // through unchanged.
  toleranceNotice: string | null = null;

  // the widgets themselves, so a value held at the limit can be put back on
  // screen (see showInInput)
  @ViewChild('topToleranceInput') topToleranceInput: InputNumber;
  @ViewChild('bottomToleranceInput') bottomToleranceInput: InputNumber;

  // the spinners fire on every step, and each committed depth reloads the
  // station map, so let the value settle before acting on it
  private depthEdited$ = new Subject<void>();
  private tolerancesEdited$ = new Subject<void>();
  private destroyed$ = new Subject<void>();

  ngOnInit(): void {
    this.depthEdited$.pipe(debounceTime(400), takeUntil(this.destroyed$))
      .subscribe(() => this.commitDepth());
    this.tolerancesEdited$.pipe(debounceTime(400), takeUntil(this.destroyed$))
      .subscribe(() => this.commitTolerances());

    this.depthFilterModel$?.pipe(takeUntil(this.destroyed$))
      .subscribe(model => {
        if (model) {
          this.readInto(model, (from, to) => {
            this.depthFrom = from;
            this.depthTo = to;
          });
        }
      });

    this.tolerancesFilterModel$?.pipe(takeUntil(this.destroyed$))
      .subscribe(model => {
        if (model) {
          this.readInto(model, (top, bottom) => {
            this.topTolerance = top;
            this.bottomTolerance = bottom;
          });
        }
      });
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
  }

  /**
   * Both filters store their two numbers as one "a,b" string. Seed from the
   * filter's default, then follow whatever the model currently holds - which is
   * how a reloaded validation gets its saved values back.
   */
  private readInto(model: FilterModel,
                   assign: (first: number, second: number) => void): void {
    const apply = (parameters: string) => {
      const values = (parameters ?? '').split(',');
      if (values.length === 2) {
        assign(Number(values[0]), Number(values[1]));
      }
    };

    apply(model.filterDto.default_parameter);
    model.parameters$.pipe(takeUntil(this.destroyed$)).subscribe(apply);
  }

  onDepthEdited(): void {
    // a limit quoted from the old range no longer holds; if the new one is too
    // narrow, committing it raises a notice of its own
    this.toleranceNotice = null;
    this.depthEdited$.next();
  }

  onTopToleranceEdited(value: number | null): void {
    this.topTolerance = this.withinLimit('top', value, this.topToleranceInput);
    this.tolerancesEdited$.next();
  }

  onBottomToleranceEdited(value: number | null): void {
    this.bottomTolerance = this.withinLimit('bottom', value, this.bottomToleranceInput);
    this.tolerancesEdited$.next();
  }

  /**
   * The two bands may meet but not overlap, so a tolerance can only grow into
   * the room the other one leaves. An edit past that is held at the limit and
   * explained, so a spinner held down stops at the last value that fits.
   *
   * This is done here rather than with the widget's own [max], which clamps
   * without emitting anything and so leaves nothing to raise the warning on.
   */
  private withinLimit(edge: BandEdge, value: number | null,
                      input: InputNumber | undefined): number | null {
    const max = this.maxTolerance(edge);
    if (value == null || max == null || this.toCm(value) <= this.toCm(max)) {
      this.toleranceNotice = null;
      return value;
    }

    const other: BandEdge = edge === 'top' ? 'bottom' : 'top';
    const label = edge === 'top' ? 'Top' : 'Bottom';
    this.toleranceNotice =
      `${label} tolerance can be at most ${this.trim(max)} m here, or the ${edge} band ` +
      `would overlap the ${other} band. Reduce the ${other} tolerance or widen the ` +
      `depth range to make room.`;
    this.showInInput(input, max);
    return max;
  }

  /**
   * The largest tolerance this edge can take without its band reaching into
   * the other one: the depth range, less the other tolerance. Null while the
   * range is inverted, which has a warning of its own and no room to share.
   */
  private maxTolerance(edge: BandEdge): number | null {
    const range = this.rangeCm();
    if (range < 0) {
      return null;
    }
    const other = edge === 'top' ? this.bottomTolerance : this.topTolerance;
    return Math.max(0, range - this.toCm(other)) / 100;
  }

  /**
   * The widget has already drawn the value it was given, and the model
   * binding will not redraw it when the bound value does not change - as it
   * does not when a spinner is pressed while already at the limit - so put
   * the limit on screen directly.
   */
  private showInInput(input: InputNumber | undefined, value: number): void {
    if (!input?.input) {
      return;
    }
    input.value = value;
    input.input.nativeElement.value = input.formatValue(value);
    input.input.nativeElement.setAttribute('aria-valuenow', String(value));
  }

  // Leaving a field commits straight away rather than waiting out the
  // debounce, so a value typed and then immediately validated cannot be
  // missed. Committing twice is harmless; both writes are the same.
  onDepthBlur(): void {
    this.commitDepth();
  }

  onTolerancesBlur(): void {
    this.commitTolerances();
  }

  private commitDepth(): void {
    const model = this.depthFilterModel$?.value;
    if (!model) {
      return;
    }
    // round before storing, not just before displaying: this string is what
    // reaches the backend and what the results summary prints back verbatim,
    // and stepping by 0.01 lands on values like 0.11000000000000001
    const from = this.round(this.depthFrom);
    const to = this.round(this.depthTo);
    model.parameters$.next(`${from},${to}`);
    this.depthSelectionChanged.emit(`${from};${to}`);
    this.fitTolerancesToRange();
  }

  /**
   * A narrower depth range can leave the two bands overlapping. Cut both
   * tolerances down in proportion, rounding down, so they fit again and the
   * split between them is kept.
   *
   * An empty or inverted range is left alone: that is mostly a field caught
   * halfway through being retyped, and shrinking to fit it would zero the
   * tolerances for good. The overlap and inverted-range warnings cover it
   * if it is left that way.
   */
  private fitTolerancesToRange(): void {
    if (!this.isMergeEnabled()) {
      return;
    }
    const range = this.rangeCm();
    const top = this.toCm(this.topTolerance);
    const bottom = this.toCm(this.bottomTolerance);
    if (range <= 0 || top + bottom <= range) {
      return;
    }
    // whole centimetres throughout, so the division cannot land a hair below
    // a whole number and be floored a step too far
    this.topTolerance = Math.floor(top * range / (top + bottom)) / 100;
    this.bottomTolerance = Math.floor(bottom * range / (top + bottom)) / 100;
    this.toleranceNotice =
      'The depth range is now too narrow for the tolerances, so both were ' +
      'reduced to keep the bands from overlapping.';
    this.commitTolerances();
  }

  private commitTolerances(): void {
    const model = this.tolerancesFilterModel$?.value;
    if (!model) {
      return;
    }
    const top = this.round(this.topTolerance);
    const bottom = this.round(this.bottomTolerance);
    model.parameters$.next(`${top},${bottom}`);
    this.tolerancesSelectionChanged.emit(`${top};${bottom}`);
  }

  /**
   * Whether sensor merging is on. Read straight off the model rather than
   * cached: reloading a saved validation sets `enabled` in place without the
   * subject re-emitting, so a cached copy would silently miss it.
   */
  isMergeEnabled(): boolean {
    return this.tolerancesFilterModel$?.value?.enabled ?? false;
  }

  isMergeBlocked(): boolean {
    return !!this.mergeBlockedReason && !this.isMergeEnabled();
  }

  /**
   * Merging is carried by whether the tolerances filter is enabled, so this
   * toggle is the whole switch - the tolerance values are only consulted when
   * it is on.
   */
  toggleMergeStations(enabled: boolean): void {
    const model = this.tolerancesFilterModel$?.value;
    if (!model) {
      return;
    }
    model.enabled = enabled;
    if (enabled) {
      // start from two bands that share the range evenly, each tolerance half
      // of it rounded down to the 0.01 m the fields step in, so the bands meet
      // in the middle at most and never overlap
      const half = Math.floor(Math.max(0, this.rangeCm()) / 2) / 100;
      this.topTolerance = half;
      this.bottomTolerance = half;
    }
    this.toleranceNotice = null;
    this.commitTolerances();
  }

  /** e.g. "0-0.1 m", shown next to the depth arrows */
  depthRangeLabel(): string {
    return `${this.trim(this.depthFrom)}–${this.trim(this.depthTo)} m`;
  }

  /**
   * Where a sensor has to sit to anchor the top of the profile.
   *
   * Each tolerance forms a band around its own depth boundary - it is not one
   * span running from the top boundary to the bottom one. A station qualifies
   * only if it has a sensor in this band and another in the bottom band.
   */
  topBandLabel(): string {
    return this.bandLabel(this.depthFrom, this.topTolerance);
  }

  /** the same, around the lower boundary, using the bottom tolerance */
  bottomBandLabel(): string {
    return this.bandLabel(this.depthTo, this.bottomTolerance);
  }

  private bandLabel(depth: number, tolerance: number): string {
    // a band never reaches above the surface, so the shallow edge clamps at 0
    const from = Math.max(0, depth - tolerance);
    const to = depth + tolerance;
    return `${this.trim(from)}–${this.trim(to)} m`;
  }

  /** true when the range is inverted, which the backend refuses to run */
  hasInvalidRange(): boolean {
    return this.depthTo < this.depthFrom;
  }

  /**
   * True when the bands overlap. Edits here cannot get there, but a
   * validation saved before the bands were kept apart can come back like
   * that - the old default was 0.1 m each on a 0-0.1 m range.
   */
  bandsOverlap(): boolean {
    return this.toCm(this.topTolerance) + this.toCm(this.bottomTolerance) > this.rangeCm();
  }

  /** the depth range in whole centimetres, negative when it is inverted */
  private rangeCm(): number {
    return this.toCm(this.depthTo) - this.toCm(this.depthFrom);
  }

  /**
   * Whole centimetres, which every value here is a whole number of, so the
   * band arithmetic is exact. A cleared field (null) counts as 0.
   */
  private toCm(metres: number | null): number {
    return Math.round((metres ?? 0) * 100);
  }

  private trim(metres: number): string {
    return String(this.round(metres));
  }

  /**
   * Two decimals, which is also the finest these fields can be stepped to.
   * Binary floating point makes 0.1 + 0.01 into 0.11000000000000001, and that
   * would otherwise show up in the panel, in the stored filter parameter and
   * in the results summary.
   */
  private round(metres: number): number {
    return Math.round(metres * 100) / 100;
  }
}
