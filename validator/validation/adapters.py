import warnings
import numpy as np
import pandas as pd
from scipy.stats import theilslopes
from pytesmo.validation_framework.metric_calculators_adapters import SubsetsMetricsAdapter

class StabilityMetricsAdapter(SubsetsMetricsAdapter):
    """
    Extend SubsetsMetricsAdapter to calculate additional stability metrics 
    (e.g., Theil-Sen slopes) for specific metrics across temporal subsets.
    """

    SUPPORTED_METRICS_FOR_SLOPES = ['R', 'BIAS', 'urmsd']

    def __init__(self, calculator, subsets, group_results='tuple'):
        """
        Initialize the StabilityMetricsAdapter.

        Parameters
        ----------
        calculator : Metric calculator instance (e.g., PairwiseIntercomparisonMetrics or TripleCollocationMetrics)
            The base metric calculator to adapt.
        subsets : dict[str, TsDistributor]
            Define subsets of data, with group names as keys and a data distributor as values.
        group_results: str, optional (default: 'tuple')
            How to group the results.
            - 'tuple' will group the results by (group, metric)
            - 'join' will join group and metric name with a '|'
        """
        super().__init__(calculator, subsets, group_results)

    def calc_metrics(self, data, gpi_info):
        """
        Calculate the base metrics for each subset, then calculate Theil-Sen slopes
        for specific metrics across all subsets that have a '|' in the key, except "bulk".

        Parameters
        ----------
        data : pandas.DataFrame
            Data with 2 columns: 'ref' (reference dataset) and 'other' (comparison dataset).
        gpi_info : tuple
            Grid point info (gpi, lon, lat).

        Returns
        -------
        dict :
            Dictionary containing calculated base metrics and Theil-Sen slopes.
        """
        dataset = self.result_template.copy()

        # First, calculate and store base metrics for each subset
        for setname, distr in self.subsets.items():
            if len(data.index) == 0:
                df = data
            else:
                df = distr.select(data)  # Filter data by the current subset

            # Calculate base metrics using the wrapped metric calculator
            base_metrics = self.cls.calc_metrics(df, gpi_info=gpi_info)

            # Store the base metrics in the dataset
            for metric, res in base_metrics.items():
                k = self._genname(setname, metric)
                dataset[k] = res

        # After storing all base metrics, calculate Theil-Sen slopes for specific metrics
        stability_metrics = self._calculate_stability_metrics(dataset)

        # Merge stability metrics into the dataset
        dataset.update(stability_metrics)

        return dataset

    def _calculate_stability_metrics(self, dataset):
        """
        Calculate Theil-Sen slopes for specific metrics ('R', 'BIAS', 'urmsd')
        across time subsets where the key contains a '|', except if the "year" part is 'bulk'.

        Parameters
        ----------
        dataset : dict
            Dictionary of base metrics for each time subset and metric.

        Returns
        -------
        dict :
            Dictionary containing Theil-Sen slopes for the specified metrics across time.
        """
        stability_results = {}

        # Group metrics by type (e.g., 'R', 'BIAS', 'urmsd') and fit Theil-Sen slopes across time
        metrics_by_type = {}

        for key, value in dataset.items():
            # Only process keys that contain a '|' and ignore the 'bulk' case
            if '|' in key:
                year, metric_name = key.split('|')

                # Skip entries where the "year" is labeled as "bulk"
                if year == "bulk":
                    continue

                # Only calculate Theil-Sen slopes for specific metrics
                if metric_name not in self.SUPPORTED_METRICS_FOR_SLOPES:
                    continue

                # Group the values by the metric name (e.g., 'R', 'BIAS', 'urmsd')
                if metric_name not in metrics_by_type:
                    metrics_by_type[metric_name] = []
                metrics_by_type[metric_name].append((int(year), value))  # Store year and value

        # Now calculate Theil-Sen slope for each supported metric type
        for metric_name, entries in metrics_by_type.items():
            # Sort entries by year
            sorted_entries = sorted(entries, key=lambda x: x[0])
            years = np.array([entry[0] for entry in sorted_entries])
            values = np.array([entry[1] for entry in sorted_entries])

            # mask where the values are not NaN
            flattened_values = values.flatten() 
            valid_mask = ~np.isnan(flattened_values)
            valid_years = years[valid_mask]
            valid_values = flattened_values[valid_mask] 

            #slopeurmsd is not as easy to read as slopeURMSD
            if metric_name == 'urmsd':
                metric_name = metric_name.upper()
            try:
                slope, _, _, _ = theilslopes(valid_values, valid_years)
                slope_per_decade = slope * 10

                # Store the slope results for this metric type
                stability_results[f'bulk|slope{metric_name}'] = np.array([slope_per_decade])

            except Exception as e:
                stability_results[f'bulk|slope{metric_name}'] = np.array([np.nan])
                warnings.warn(f"Failed to calculate Theil-Sen slope for {metric_name}: {e}")

        return stability_results
