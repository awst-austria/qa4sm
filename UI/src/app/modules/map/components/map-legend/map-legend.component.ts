import {Component, Input,} from '@angular/core';
import {LegendItem} from '../legend-item';
import {DomSanitizer} from '@angular/platform-browser';


@Component({
    selector: 'qa-map-legend',
    templateUrl: './map-legend.component.html',
    styleUrls: ['./map-legend.component.scss'],
    standalone: false
})
export class MapLegendComponent {
  @Input() legendItems: LegendItem[] = [];

  constructor(private sanitizer: DomSanitizer)  { }


  getCircleSVG(properties: LegendItem): any {
    const { radius, fillColor, strokeColor, strokeWidth } = properties;
    const actualFillColor = fillColor || 'transparent';
    const actualStrokeColor = strokeColor || actualFillColor;

    const svg = `<svg width="${3 * radius}" height="${3 * radius}">
                  <circle cx="${1.5 * radius}" cy="${1.5 * radius}" r="${radius}"
                          fill="${actualFillColor}"
                          stroke="${actualStrokeColor}"
                          stroke-width="${strokeWidth}" />
                </svg>`;

    return this.sanitizer.bypassSecurityTrustHtml(svg);
  }

}
