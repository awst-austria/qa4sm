import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AccordionModule } from 'primeng/accordion';
import { SelectModule } from 'primeng/select';
import { FloatLabelModule } from 'primeng/floatlabel';

interface AutoReport {
  filename: string;
  report_date: string;        // '20260131'
  creation_date: string;      // '202606290613'
  report_date_iso: string;    // '2026-01-31'
  indicator: 'G' | 'Y' | 'R';
}

interface YearGroup {
  year: string;
  months: (AutoReport | null)[];   // indexes 0..11 = Jan..Dec
}

@Component({
  selector: 'qa-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, AccordionModule, SelectModule, FloatLabelModule],
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss'],
})
export class ReportsComponent implements OnInit {
  private http = inject(HttpClient);

  seriesList: string[] = [];
  selectedSeries: string | null = null;
  yearGroups: YearGroup[] = [];
  activeYears: string[] = [];
  loading = false;

  readonly monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  readonly seriesSelectorId = 'report-series-selector';

  ngOnInit(): void {
    this.http.get<string[]>('/api/autoreports').subscribe(series => {
      this.seriesList = series;
      if (series.length) {
        this.loadSeries(series[0]);   // auto-select the first series
      }
    });
  }

  loadSeries(series: string): void {
    this.selectedSeries = series;
    this.loading = true;
    this.http.get<AutoReport[]>(`/api/autoreports/${series}`).subscribe({
      next: reports => {
        this.yearGroups = this.groupByYear(reports);
        // expand the most recent year by default
        this.activeYears = this.yearGroups.length ? [this.yearGroups[0].year] : [];
        this.loading = false;
      },
      error: () => {
        this.yearGroups = [];
        this.activeYears = [];
        this.loading = false;
      }
    });
  }

  private groupByYear(reports: AutoReport[]): YearGroup[] {
    const byYear = new Map<string, (AutoReport | null)[]>();
    for (const report of reports) {
      const year = report.report_date.slice(0, 4);
      const monthIdx = parseInt(report.report_date.slice(4, 6), 10) - 1;
      if (!byYear.has(year)) {
        byYear.set(year, Array(12).fill(null));
      }
      byYear.get(year)![monthIdx] = report;
    }
    return [...byYear.entries()]
      .sort((a, b) => b[0].localeCompare(a[0]))     // newest year first
      .map(([year, months]) => ({ year, months }));
  }

  indicatorCount(group: YearGroup, indicator: 'G' | 'Y' | 'R'): number {
    return group.months.filter(m => m?.indicator === indicator).length;
  }

  formatCreation(creationDate: string): string {
    // '202606290613' -> '2026-06-29 06:13'
    return `${creationDate.slice(0, 4)}-${creationDate.slice(4, 6)}-${creationDate.slice(6, 8)}`
         + ` ${creationDate.slice(8, 10)}:${creationDate.slice(10, 12)}`;
  }

  reportUrl(report: AutoReport): string {
    return `/api/autoreports/${this.selectedSeries}/${report.filename}`;
  }
}