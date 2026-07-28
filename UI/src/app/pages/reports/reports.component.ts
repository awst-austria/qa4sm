import { Component, DestroyRef, OnDestroy, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';

import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AccordionModule } from 'primeng/accordion';
import { SelectModule } from 'primeng/select';
import { FloatLabelModule } from 'primeng/floatlabel';
import { CommonModule } from '@angular/common';

interface AutoReport {
  filename: string;
  report_date: string; // '20260131'
  creation_date: string; // '202606290613'
  report_date_iso: string; // '2026-01-31'
  indicator: 'G' | 'Y' | 'R' | null; // null when the filename carries no indicator
}

interface YearGroup {
  year: string;
  reports: AutoReport[]; // newest first; sampling may be irregular
}

@Component({
  selector: 'qa-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, AccordionModule, SelectModule, FloatLabelModule],
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss'],
})
export class ReportsComponent implements OnInit, OnDestroy {
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);

  seriesList: string[] = [];
  selectedSeries: string | null = null;
  yearGroups: YearGroup[] = [];
  activeYears: string[] = [];
  loading = false;
  latestReport: AutoReport | null = null;
  copiedUrl: string | null = null;
  private copyResetTimer?: ReturnType<typeof setTimeout>;

  readonly indicatorLabels: Record<'G' | 'Y' | 'R', string> = {
    G: 'Good — no issues detected',
    Y: 'Warning — review recommended',
    R: 'Critical — action required',
  };

  readonly seriesSelectorId = 'report-series-selector';

  ngOnInit(): void {
    this.http.get<string[]>('/api/autoreports').subscribe(series => {
      this.seriesList = series;
      // The URL is the single source of truth for the selected series:
      // the dropdown navigates, and this subscription reacts to the URL.
      this.route.paramMap
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe((params) => {
          const requested = params.get('series');
          if (requested && series.includes(requested)) {
            this.loadSeries(requested);
          } else if (series.length) {
            // no or unknown series in the URL -> normalize to the first one
            this.router.navigate(['/reports', series[0]], { replaceUrl: true });
          }
        });
    });
  }

  onSeriesChange(series: string): void {
    this.router.navigate(['/reports', series]);
  }

  ngOnDestroy(): void {
    clearTimeout(this.copyResetTimer);
  }

  loadSeries(series: string): void {
    this.selectedSeries = series;
    this.loading = true;
    this.http.get<AutoReport[]>(`/api/autoreports/${series}`).subscribe({
      next: (reports) => {
        const sorted = [...reports].sort((a, b) =>
          b.report_date.localeCompare(a.report_date),
        );
        this.latestReport = sorted[0] ?? null;
        this.yearGroups = this.groupByYear(sorted);
        // expand the most recent year by default
        this.activeYears = this.yearGroups.length ? [this.yearGroups[0].year] : [];
        this.loading = false;
      },
      error: () => {
        this.latestReport = null;
        this.yearGroups = [];
        this.activeYears = [];
        this.loading = false;
      }
    });
  }

  private groupByYear(sortedReports: AutoReport[]): YearGroup[] {
    const byYear = new Map<string, AutoReport[]>();
    for (const report of sortedReports) {
      const year = report.report_date.slice(0, 4);
      if (!byYear.has(year)) {
        byYear.set(year, []);
      }
      byYear.get(year)!.push(report);
    }
    // input is sorted newest-first, so Map insertion order is already
    // newest year first and reports within a year are newest first
    return [...byYear.entries()].map(([year, reports]) => ({ year, reports }));
  }

  indicatorCount(group: YearGroup, indicator: 'G' | 'Y' | 'R'): number {
    return group.reports.filter((r) => r.indicator === indicator).length;
  }

  indicatorTitle(report: AutoReport): string {
    return report.indicator
      ? this.indicatorLabels[report.indicator]
      : 'No indicator provided';
  }

  formatCreation(creationDate: string): string {
    // '202606290613' -> '2026-06-29 06:13'
    return `${creationDate.slice(0, 4)}-${creationDate.slice(4, 6)}-${creationDate.slice(6, 8)}`
         + ` ${creationDate.slice(8, 10)}:${creationDate.slice(10, 12)}`;
  }

  reportUrl(report: AutoReport): string {
    return `/api/autoreports/${this.selectedSeries}/${report.filename}`;
  }

  latestUrl(): string {
    return `/api/autoreports/${this.selectedSeries}/latest`;
  }

  async copyLink(path: string): Promise<void> {
    const absolute = new URL(path, window.location.origin).toString();
    try {
      await navigator.clipboard.writeText(absolute);
      this.copiedUrl = path;
      clearTimeout(this.copyResetTimer);
      this.copyResetTimer = setTimeout(() => (this.copiedUrl = null), 2000);
    } catch {
      // clipboard unavailable 
    }
  }
}