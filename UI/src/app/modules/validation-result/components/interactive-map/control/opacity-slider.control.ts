import Control from 'ol/control/Control';
import TileLayer from 'ol/layer/Tile';

export interface OpacitySliderOptions {
  initialOpacity?: number;
}

export class OpacitySliderControl extends Control {
  private slider: HTMLInputElement;
  private layer: TileLayer<any> | null = null;

  constructor(options: OpacitySliderOptions = {}) {
    const element = document.createElement('div');
    element.className = 'ol-opacity-slider ol-unselectable ol-control';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.min = '0';
    slider.max = '1';
    slider.step = '0.01';
    slider.value = String(options.initialOpacity ?? 0.7);

    const label = document.createElement('label');
    label.textContent = 'Opacity';

    element.appendChild(label);
    element.appendChild(slider);

    super({ element });

    this.slider = slider;

    // Use arrow function to preserve 'this' context
    this.slider.addEventListener('input', () => this.onSliderChange());
  }

  private onSliderChange(): void {
    const opacity = parseFloat(this.slider.value);
    if (this.layer) {
      this.layer.setOpacity(opacity);
    }
  }

  setLayer(layer: TileLayer<any>): void {
    this.layer = layer;
    // Sync slider to layer's current opacity
    this.slider.value = String(layer.getOpacity());
  }

  getSliderValue(): number {
    return parseFloat(this.slider.value);
  }
}
