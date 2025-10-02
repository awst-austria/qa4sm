import { Control } from 'ol/control';

export class LegendControl extends Control {
  private legendElement: HTMLElement;
  private contentElement: HTMLElement;

  constructor(options: any = {}) {
    const element = document.createElement('div');
    element.className = 'ol-legend ol-unselectable ol-control';

    super({
      element: element,
      target: options.target,
    });

    this.legendElement = element;
    this.contentElement = document.createElement('div');
    this.contentElement.className = 'legend-content';
    this.legendElement.appendChild(this.contentElement);

    this.updateLegend(options.colorbarData, options.metricName);
  }

  updateLegend(colorbarData: any, metricName: string) {
    // Clear and hide if no data
    if (!colorbarData || !colorbarData.legend_data) {
      this.legendElement.style.display = 'none';
      this.contentElement.innerHTML = '';
      return;
    }

    // Show legend
    this.legendElement.style.display = 'block';

    // Build legend HTML
    const legendHTML = this.buildLegendHTML(colorbarData, metricName);
    this.contentElement.innerHTML = legendHTML;
  }

  private buildLegendHTML(colorbarData: any, metricName: string): string {
    const legendData = colorbarData.legend_data;

    if (!legendData || !legendData.entries || legendData.entries.length === 0) {
      return '<div class="legend-empty">No legend data available</div>';
    }

    // Build title
    const title = `<div class="legend-title">${this.escapeHtml(metricName || 'Legend')}</div>`;

    // Build legend items
    const items = legendData.entries
      .map((entry: any) => this.buildLegendItem(entry))
      .join('');

    return `
      ${title}
      <div class="legend-items">
        ${items}
      </div>
    `;
  }


 private buildLegendItem(entry: any): string {
  const color = entry.color || '#cccccc';
  const label = this.escapeHtml(entry.label || 'Unknown');

  return `
    <div class="legend-item">
      <div class="legend-symbol" style="background-color: ${color};"></div>
      <span class="legend-label">${label}</span>
    </div>
  `;
}


  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  hide() {
    this.legendElement.style.display = 'none';
  }

  show() {
    this.legendElement.style.display = 'block';
  }
}
