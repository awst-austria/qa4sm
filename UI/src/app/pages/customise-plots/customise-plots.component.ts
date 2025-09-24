import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'qa-customise-plots',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './customise-plots.component.html',
  styleUrl: './customise-plots.component.scss'
})
export class CustomisePlotsComponent {

  copy(id: string) {
    const el = document.getElementById(id) as HTMLTextAreaElement | null;
    if (!el) return;
    el.select();
    el.setSelectionRange(0, el.value.length);
    navigator.clipboard?.writeText(el.value);
  }

  DownloadJupiterNotebook() {
    const filePath = '/static/images/customplots/custom_plots.tar.gz';

    // Create an invisible anchor and trigger click
    const link = document.createElement('a');
    link.href = filePath;
    link.download = 'custom_plots.tar.gz'; 
    link.click();
  }

  steps = [
  {
    title: 'Step 1',
    description: 'Before you can start your plots execute the following cell once to install the necessary packages.',
    code: `%pip install qa4sm-reader`,
    image: null
  },
  {
    title: 'Step 2',
    description: 'Load data and display valid metrics and datasets in the NetCDF data.',
    code: `from qa4sm_reader.custom_user_plot_generator import CustomPlotObject
import os

# Create Custom_Plot_object
dataset_name = "0-ERA5_LAND.swvl1_with_1-C3S_combined.sm.nc"
dataset_path = os.path.join(os.getcwd(), 'data', dataset_name)
output_path = os.path.join(os.getcwd(), 'output')
plot_obj = CustomPlotObject(dataset_path)
plot_obj.display_metrics_and_datasets()`,
    image: null
  },
  {
    title: 'Step 3',
    description: 'Create default plot',
    code: `plot_obj.plot_map(metric='R', output_dir=output_path, dataset_list=['ERA5_LAND','C3S_combined'])`,
    image: '/static/images/customplots/imageStep3.webp'
  },
  {
    title: 'Step 4',
    description: 'Customize colorbar and set custom Value Range. Popular colorbar choices are: viridis, plasma, inferno, magma, cividis, PiYG, PRGn, BrBG, PuOr, RdGy, RdBu, RdYlBu, RdYlGn, Spectral, coolwarm, cividis. For further information regarding colormaps go to the respective website of matplotlib',
    code: `plot_obj.plot_map(metric='R', output_dir=output_path, dataset_list=['ERA5_LAND', 'C3S_combined'], colormap="viridis", value_range=(-0.5, 0.5))`,
    image: '/static/images/customplots/imageStep4.webp'
  },
  {
    title: 'Step 5',
    description: 'Change spatial extent of plot. The extent is set as (lon_min, lon_max, lat_min, lat_max)',
    code: `plot_obj.plot_map(metric='R', output_dir=output_path, dataset_list=['ERA5_LAND', 'C3S_combined'], colormap="viridis", extent=(-10, 20, 30, 40))`,
    image: '/static/images/customplots/imageStep5.webp'
  },
  {
    title: 'Step 6',
    description: 'Custom Title and Colorbar label and adjusted tick label sizes.',
    code: `plot_obj.plot_map(metric='R', output_dir=output_path, dataset_list=['ERA5_LAND', 'C3S_combined'], title='Pearson Correlation between ERA5_Land and C3S_combined', title_fontsize=20,  colorbar_label='Pearson Correlation Coefficient', colorbar_ticks_fontsize=20,
xy_ticks_fontsize=20)`,
    image: '/static/images/customplots/imageStep6.webp'
  },
  {
    title: 'Step 7',
    description: 'Custom Title and Colorbar label and adjusted tick label sizes.',
    code: `plot_obj.plot_map(metric='R', output_dir=output_path, dataset_list=['ERA5_LAND', 'C3S_combined'], plotsize=(20, 10))`,
    image: '/static/images/customplots/imageStep7.webp'
  },
  {
    title: 'Step 8',
    description: 'Special Case - Triple collocation variables (snr, beta, err_std). Note that for those metrics only the dataset name of interest is passed to the dataset list as an input (e.g. "ISMN" for the snr-value of ISMN relative to the other datasets")!',
    code: `# Create Custom_Plot_object
tc_dataset_name = "0-ISMN.soil_moisture_with_1-ERA5_LAND.swvl1_with_2-ESA_CCI_SM_passive.sm.nc"
tc_dataset_path = os.path.join(os.getcwd(), 'data', tc_dataset_name)
tc_plot_obj = CustomPlotObject(tc_dataset_path)
tc_plot_obj.display_metrics_and_datasets()
tc_plot_obj.plot_map(metric='snr', output_dir=output_path, dataset_list=['ISMN'], title='ISMN SNR relative to ERA5_LAND and ESA_CCI_SM_passive', title_fontsize=20, colorbar_label='SNR', colorbar_ticks_fontsize=20, xy_ticks_fontsize=20)`,
    image: null
  },
];


}
