import { Component,Input, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

type UIParamFilter = { id: number | null; parameters: string };
type UIDataset = {
  dataset_id: number | null;
  variable_id: number | null;
  version_id: number | null;
  basic_filters_csv: string; // user types "1,2,3"
  parametrised_filters: UIParamFilter[];
  is_spatial_reference: boolean;
  is_temporal_reference: boolean;
  is_scaling_reference: boolean;
};

@Component({
  selector: 'qa-json-config',
  standalone: true,
  imports: [RouterLink, CommonModule, FormsModule],
  templateUrl: './json-config.component.html',
  styleUrl: './json-config.component.scss'
})
export class JsonConfigComponent {

  // UI state with defaults prefilled
  ui = {
    interval_from_local: '1978-11-01T00:00',
    interval_to_local: '2024-12-31T00:00',

    min_lat: 34,
    max_lat: 71.6,
    min_lon: -11.2,
    max_lon: 48.3,

    temporal_matching: 12,

    scaling_method: 'none',
    scale_to: '0',

    anomalies_method: 'none' as 'none' | 'climatology',
    anom_from_local: '1899-12-31T23:00',
    anom_to_local: '1900-12-30T23:00',

    metrics: {
      tcol: false,
      bootstrap_tcol_cis: false,
      stability_metrics: false
    },

    intra: {
      enabled: false,
      type: '',
      overlap: null as number | null
    },

    name_tag: '',

    datasets: [
      {
        dataset_id: 4,
        variable_id: 4,
        version_id: 69,
        basic_filters_csv: '1,2',
        parametrised_filters: [
          {
            id: 18,
            parameters:
              'AMMA-CATCH,DAHRA,TAHMO,SD_DEM,CHINA,CTP_SMTMN,HiWATER_EHWSN,HSC_SEOLMACHEON,IIT_KANPUR,KHOREZM,MAQU,MONGOLIA,MySMNet,RUSWET-AGRO,RUSWET-GRASS,RUSWET-VALDAI,SKKU,SW-WHU,KIHS_CMC,KIHS_SMC,VDS,NAQU,NGARI,SMN-SDR,SONTE-China,WIT-Network,AACES,OZNET,SASMAS,BIEBRZA_S-1,CALABRIA,CAMPANIA,FMI,FR_Aqui,GROW,GTK,HOBE,HYDROL-NET_PERUGIA,IMA_CAN1,METEROBS,MOL-RAO,ORACLE,REMEDHUS,RSMN,SMOSMANIA,SWEX_POLAND,TERENO,UDC_SMOS,UMBRIA,UMSUOL,VAS,WEGENERNET,WSMN,HOAL,IPE,COSMOS-UK,LABFLUX,NVE,Ru_CFR,STEMS,TWENTE,XMS-CAT,ARM,AWDN,BNZ-LTER,FLUXNET-AMERIFLUX,ICN,IOWA,PBO_H2O,RISMA,SCAN,SNOTEL,SOILSCAPE,USCRN,USDA-ARS,TxSON,LAB-net,PTSMN'
          },
          { id: 24, parameters: '0.00,0.10' }
        ],
        is_spatial_reference: true,
        is_temporal_reference: false,
        is_scaling_reference: false
      },
      {
        dataset_id: 1,
        variable_id: 1,
        version_id: 70,
        basic_filters_csv: '1',
        parametrised_filters: [],
        is_spatial_reference: false,
        is_temporal_reference: true,
        is_scaling_reference: false
      }
    ] as UIDataset[]
  };

  lastDownloadName = '';
  previewJson = '';

  // Helpers for datasets/param filters
  addDataset() {
    this.ui.datasets.push({
      dataset_id: null,
      variable_id: null,
      version_id: null,
      basic_filters_csv: '',
      parametrised_filters: [],
      is_spatial_reference: false,
      is_temporal_reference: false,
      is_scaling_reference: false
    });
  }
  removeDataset(i: number) {
    this.ui.datasets.splice(i, 1);
  }
  addParamFilter(datasetIndex: number) {
    this.ui.datasets[datasetIndex].parametrised_filters.push({ id: null, parameters: '' });
  }
  removeParamFilter(datasetIndex: number, pfIndex: number) {
    this.ui.datasets[datasetIndex].parametrised_filters.splice(pfIndex, 1);
  }

  // Build the final JSON object from UI state
  private buildConfig() {
    const toISO = (local: string) => {
      // convert 'YYYY-MM-DDTHH:mm' (local) to ISO UTC with Z
      const d = new Date(local);
      return isNaN(d.getTime()) ? '' : d.toISOString();
    };

    const dataset_configs = this.ui.datasets.map(d => ({
      dataset_id: Number(d.dataset_id),
      variable_id: Number(d.variable_id),
      version_id: Number(d.version_id),
      basic_filters:
        d.basic_filters_csv
          .split(',')
          .map(s => s.trim())
          .filter(Boolean)
          .map(n => Number(n)),
      parametrised_filters: d.parametrised_filters
        .filter(p => p.id !== null && p.parameters?.trim())
        .map(p => ({ id: Number(p.id), parameters: p.parameters.trim() })),
      is_spatial_reference: !!d.is_spatial_reference,
      is_temporal_reference: !!d.is_temporal_reference,
      is_scaling_reference: !!d.is_scaling_reference
    }));

    const metrics = [
      { id: 'tcol', value: !!this.ui.metrics.tcol },
      { id: 'bootstrap_tcol_cis', value: !!this.ui.metrics.bootstrap_tcol_cis },
      { id: 'stability_metrics', value: !!this.ui.metrics.stability_metrics }
    ];

    const config = {
      dataset_configs,
      interval_from: toISO(this.ui.interval_from_local),
      interval_to: toISO(this.ui.interval_to_local),
      min_lat: Number(this.ui.min_lat),
      min_lon: Number(this.ui.min_lon),
      max_lat: Number(this.ui.max_lat),
      max_lon: Number(this.ui.max_lon),
      metrics,
      intra_annual_metrics: {
        intra_annual_metrics: !!this.ui.intra.enabled,
        intra_annual_type: this.ui.intra.type || '',
        intra_annual_overlap: this.ui.intra.overlap ?? null
      },
      anomalies_method: this.ui.anomalies_method,
      anomalies_from: this.ui.anomalies_method === 'none' ? '1899-12-31T23:00:00.000Z' : toISO(this.ui.anom_from_local),
      anomalies_to: this.ui.anomalies_method === 'none' ? '1900-12-30T23:00:00.000Z' : toISO(this.ui.anom_to_local),
      scaling_method: this.ui.scaling_method,
      scale_to: String(this.ui.scale_to ?? '0'),
      name_tag: this.ui.name_tag || '',
      temporal_matching: Number(this.ui.temporal_matching)
    };

    this.previewJson = JSON.stringify(config, null, 2);
    return config;
  }

  // Create + trigger download
  createAndDownload() {
    const cfg = this.buildConfig();
    const blob = new Blob([JSON.stringify(cfg, null, 2)], { type: 'application/json' });
    const now = new Date();
    const fname = `qa4sm-config-${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}.json`;

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fname;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    this.lastDownloadName = fname;
  }

}
