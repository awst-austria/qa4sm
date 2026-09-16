import {Component, EventEmitter, Input, OnDestroy, OnInit, Output} from '@angular/core';
import {BehaviorSubject, Subject} from 'rxjs';
import {debounceTime, takeUntil} from 'rxjs/operators';

import {FilterModel} from '../basic-filter/filter-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';

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

  @Output() depthSelectionChanged = new EventEmitter<string>();
  @Output() tolerancesSelectionChanged = new EventEmitter<string>();

  depthFrom = 0;
  depthTo = 0.1;
  topTolerance = 0.1;
  bottomTolerance = 0.1;

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
    this.depthEdited$.next();
  }

  onTolerancesEdited(): void {
    this.tolerancesEdited$.next();
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
