import {Component, DoCheck, Input, OnInit} from '@angular/core';
import {Observable, BehaviorSubject, combineLatest} from 'rxjs';
import {map} from 'rxjs/operators';

import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';

// datasets whose depth layers may be merged. Mirrors MERGEABLE_DATASETS in
// validator/validation/globals.py - the backend re-checks it, this list only
// decides whether the panel is worth showing.
export const MERGEABLE_DATASETS = [
  'ERA5', 'ERA5_LAND', 'GLDAS', 'ESA_CCI_RZSM', 'C3S_rzsm'
];

const DEPTH_KIND_LAYER = 'layer';

@Component({
  selector: 'qa-merge-layers',
  templateUrl: './merge-layers.component.html',
  styleUrls: ['./merge-layers.component.scss'],
  standalone: false
})
export class MergeLayersComponent implements OnInit, DoCheck {

  @Input() configModel: DatasetConfigModel;

  /**
   * The dataset+version the layer list was last built for, or null while the
   * selection is still incomplete.
   *
   * Both halves matter. Keying on the version alone latches: the version can
   * arrive a change-detection pass before the dataset, and a load attempted in
   * between bails out on the missing dataset while still recording the version
   * as done — so the retry never happens and the panel stays hidden.
   */
  private loadedKey: string = null;

  /** every layer of the current version that is eligible to be merged */
  selectableLayers$ = new BehaviorSubject<DatasetVariableDto[]>([]);
  /** shown once at least two layers are ticked */
  mergedRangeLabel$: Observable<string>;
  /** hides the whole panel unless this dataset has layers worth merging */
  available$: Observable<boolean>;

  constructor(private datasetVariableService: DatasetVariableService) {
  }

  ngOnInit(): void {
    this.available$ = this.selectableLayers$.pipe(
      map(layers => layers.length > 1)
    );

    // This component sits ahead of the rest of the validate page in the same
    // template, so anything it throws during init would stop the components
    // after it from being created at all. Nothing below may assume the model
    // is populated - the dataset and version arrive asynchronously and are
    // still null on the first pass.
    if (!this.configModel?.mergedVariables$) {
      this.mergedRangeLabel$ = this.selectableLayers$.pipe(map(() => ''));
      return;
    }

    this.mergedRangeLabel$ = combineLatest([
      this.configModel.mergedVariables$, this.selectableLayers$
    ]).pipe(
      map(([selected]) => this.describeSelection(selected))
    );

    this.loadLayers();
  }

  /**
   * The dataset and version live on a plain model that the dataset selector
   * mutates in place, so there is no stream to subscribe to. Watching the
   * version id here keeps the layer list in step with it; the comparison is a
   * single number, which is cheap enough to run on every check.
   */
  ngDoCheck(): void {
    // runs on every change detection pass, so it must never throw
    if (!this.configModel?.datasetModel) {
      return;
    }

    if (this.selectionKey() === this.loadedKey) {
      return;
    }

    // Only a switch away from a complete selection discards the ticks. Going
    // from an incomplete selection to a real one is initialisation, not a
    // change - and it is exactly what happens when a saved validation is
    // reloaded, where the restored layers are put on the model before the
    // dataset and version arrive.
    if (this.loadedKey !== null) {
      // a selection made against the old version would name columns that do
      // not exist in the new one, so it cannot carry over
      this.configModel.mergedVariables$.next([]);
    }
    this.loadLayers();
  }

  /**
   * Identifies the current selection, or null while it is still incomplete.
   * Staying null until both halves are present is what stops a half-built
   * selection from being recorded as loaded.
   */
  private selectionKey(): string {
    const version = this.configModel?.datasetModel?.selectedVersion;
    const dataset = this.configModel?.datasetModel?.selectedDataset;
    if (!version || !dataset) {
      return null;
    }
    return `${dataset.id}:${version.id}`;
  }

  private loadLayers(): void {
    const version = this.configModel?.datasetModel?.selectedVersion;
    const dataset = this.configModel?.datasetModel?.selectedDataset;

    this.loadedKey = this.selectionKey();

    if (!version || !dataset || !MERGEABLE_DATASETS.includes(dataset.short_name)) {
      this.selectableLayers$.next([]);
      return;
    }

    this.datasetVariableService.getVariablesByVersion(version.id).subscribe({
      next: variables => this.selectableLayers$.next(
        (variables ?? [])
          .filter(variable => this.isMergeableLayer(variable))
          .sort((a, b) => a.depth_from - b.depth_from || a.depth_to - b.depth_to)
      ),
      // a failed variable lookup must not take the validate page with it;
      // no layers simply means the panel stays hidden
      error: () => this.selectableLayers$.next([])
    });
  }

  /**
   * Both gates the backend applies: the variable must be a disjoint layer and
   * must actually carry depths. Aggregates such as rzsm_1m span the layers they
   * subsume, so merging one with them would double-count the whole column.
   */
  private isMergeableLayer(variable: DatasetVariableDto): boolean {
    return variable.depth_kind === DEPTH_KIND_LAYER
      && variable.depth_from != null
      && variable.depth_to != null;
  }

  isSelected(variable: DatasetVariableDto): boolean {
    return this.configModel.mergedVariables$.value
      .some(selected => selected.id === variable.id);
  }

  toggle(variable: DatasetVariableDto): void {
    const selected = this.configModel.mergedVariables$.value;
    const next = this.isSelected(variable)
      ? selected.filter(other => other.id !== variable.id)
      : [...selected, variable];

    next.sort((a, b) => a.depth_from - b.depth_from);
    this.configModel.mergedVariables$.next(next);

    // the output column follows the selection rather than being chosen
    // alongside it, so the two can never disagree. Below two layers there is
    // no merge and the variable dropdown goes back to being the user's.
    if (next.length > 1) {
      this.configModel.datasetModel.selectedVariable = next[0];
    }
  }

  setWeighted(weighted: boolean): void {
    this.configModel.mergeWeighted$.next(weighted);
  }

  /** cm span for one layer, e.g. "0-10 cm" */
  layerLabel(variable: DatasetVariableDto): string {
    return `${this.cm(variable.depth_from)}-${this.cm(variable.depth_to)} cm`;
  }

  /**
   * How much this layer contributes, as a percentage of the merged range.
   * Only meaningful while weighting is on; with it off every layer counts the
   * same regardless of how thick it is.
   */
  layerWeight(variable: DatasetVariableDto): string {
    const selected = this.configModel.mergedVariables$.value;
    if (selected.length < 2 || !this.isSelected(variable)) {
      return '';
    }
    if (!this.configModel.mergeWeighted$.value) {
      return `${(100 / selected.length).toFixed(0)}%`;
    }
    const total = selected.reduce((sum, layer) => sum + this.thickness(layer), 0);
    return `${(100 * this.thickness(variable) / total).toFixed(0)}%`;
  }

  /**
   * Describes the merged selection. A gapped pick is allowed - the value stays
   * well defined because each layer is weighted by its own thickness - but a
   * single span would claim depths that contributed nothing, so those are
   * described by their members instead.
   */
  private describeSelection(selected: DatasetVariableDto[]): string {
    if (selected.length < 2) {
      return '';
    }
    const ordered = [...selected].sort((a, b) => a.depth_from - b.depth_from);

    if (this.isContiguous(ordered)) {
      const first = ordered[0];
      const last = ordered[ordered.length - 1];
      return `${this.cm(first.depth_from)}-${this.cm(last.depth_to)} cm`;
    }
    return ordered.map(layer =>
      `${this.cm(layer.depth_from)}-${this.cm(layer.depth_to)}`).join(', ') + ' cm';
  }

  isContiguous(selected: DatasetVariableDto[]): boolean {
    const ordered = [...selected].sort((a, b) => a.depth_from - b.depth_from);
    for (let i = 1; i < ordered.length; i++) {
      // depths are floats, so compare with a tolerance
      if (Math.abs(ordered[i].depth_from - ordered[i - 1].depth_to) > 1e-9) {
        return false;
      }
    }
    return true;
  }

  hasGap(): boolean {
    const selected = this.configModel.mergedVariables$.value;
    return selected.length > 1 && !this.isContiguous(selected);
  }

  isMerging(): boolean {
    return this.configModel.mergedVariables$.value.length > 1;
  }

  /**
   * The layer the merged series is written into: the shallowest ticked one.
   *
   * Read from the tick list rather than from the variable dropdown on purpose.
   * The backend derives the output column from the merge selection too, so
   * taking it from the same place means this label cannot end up claiming a
   * column the merge will not actually write to.
   */
  outputLayer(): DatasetVariableDto {
    const selected = this.configModel.mergedVariables$.value;
    if (selected.length < 2) {
      return null;
    }
    return [...selected].sort((a, b) => a.depth_from - b.depth_from)[0];
  }

  private thickness(variable: DatasetVariableDto): number {
    return variable.depth_to - variable.depth_from;
  }

  private cm(metres: number): number {
    // %g-style: 0.07 -> 7, 1 -> 100, without trailing zeroes
    return Math.round(metres * 1000) / 10;
  }
}
