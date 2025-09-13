import logging

from django.urls import reverse
from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.test import APIClient
from api.tests.test_helper import *

import validator.validation as val


@override_settings(
    CELERY_TASK_EAGER_PROPAGATES=True,
    CELERY_TASK_ALWAYS_EAGER=True
)
class TestValidationComparisonView(TestCase):
    # Test all functions in api/views/comparison_view.py
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables', 'users']

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()

        self.client = APIClient()
        self.client.login(**self.auth_data)

        self.run = default_parameterized_validation_to_be_run(self.test_user)
        self.run.name_tag = 'initial validation'
        self.run.save()

        self.run.min_lat = 18.477
        self.run.min_lon = -156.125
        self.run.max_lat = 21.127
        self.run.max_lon = -154.299

        # ---------- partially overlapping --------
        self.run_partially_overlapping = default_parameterized_validation_to_be_run(self.test_user)
        self.run_partially_overlapping.name_tag = 'partially overlapping'
        self.run_partially_overlapping.save()

        # set extent to partially overlapping
        self.run_partially_overlapping.min_lat = 19.353
        self.run_partially_overlapping.min_lon = -156.881
        self.run_partially_overlapping.max_lat = 21.673
        self.run_partially_overlapping.max_lon = -155.238

        # ---------- non overlapping --------------
        self.run_non_overlapping = default_parameterized_validation_to_be_run(self.test_user)
        self.run_non_overlapping.name_tag = 'non overlapping'
        self.run_non_overlapping.save()

        # set extent to non overlapping
        self.run_non_overlapping.min_lat = 19.623
        self.run_non_overlapping.min_lon = -158.159
        self.run_non_overlapping.max_lat = 21.988
        self.run_non_overlapping.max_lon = -156.62

        # run all validations as we need the output
        val.run_validation(self.run.id)
        val.run_validation(self.run_partially_overlapping.id)
        val.run_validation(self.run_non_overlapping.id)

        self.ids = [
            str(i) for i in (
                self.run.id,
                self.run_partially_overlapping.id,
                self.run_non_overlapping.id
            )
        ]

    def test_get_comparison_table(self):
        # Tests for the comparison statistics table generation function
        comparison_table_url = reverse('Comparison table')

        # try out several configurations
        response = self.client.get(
            comparison_table_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                   f'metric_list=R&metric_list=urmsd'
        )
        response_intersection = self.client.get(
            comparison_table_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                   f'metric_list=R&metric_list=urmsd&'
                                   f'get_intersection=true'
        )
        response_non_overl_extent = self.client.get(
            comparison_table_url + f'?ids={self.ids[0]}&ids={self.ids[2]}&'
                                   f'metric_list=R&metric_list=urmsd&'
                                   f'get_intersection=false'
        )
        response_wrong_extent = self.client.get(
            comparison_table_url + f'?ids={self.ids[0]}&ids={self.ids[2]}&'
                                   f'metric_list=R&metric_list=urmsd&'
                                   f'get_intersection=true'
        )

        assert response.status_code == 200
        assert response_intersection.status_code == 200
        assert response_non_overl_extent.status_code == 200
        assert response_wrong_extent.status_code == 200, "The response should not produce an error, but " \
                                                         "SpatialExtentErrors should be handled and return " \
                                                         "the query with 'get_intersection=false'"

    def test_download_comparison_table(self):
        down_comparison_table_url = reverse('Download comparison csv')

        response = self.client.get(
            down_comparison_table_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                        f'metric_list=R&metric_list=urmsd'
        )

        assert response.status_code == 200
        assert 'Comparison_summary.csv' in response.get('Content-Disposition')

    def test_get_comparison_metrics(self):
        metric_comparison_url = reverse('Comparison metrics')

        # try out several configurations
        response = self.client.get(
            metric_comparison_url + f'?ids={self.ids[0]}&ids={self.ids[1]}'
        )
        response_intersection = self.client.get(
            metric_comparison_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                    f'get_intersection=true'
        )

        assert response.status_code == 200
        assert response_intersection.status_code == 200
        assert response.get('Content-Length') == response_intersection.get('Content-Length')

        metric_list = response_intersection.json()
        assert len(metric_list) == 12
        metrics_query = []
        for metric in metric_list:
            assert 'metric_pretty_name' in metric.keys()
            assert 'metric_query_name' in metric.keys()
            metrics_query.append(metric['metric_query_name'])

        # get a comparison table with the so collected metrics
        metrics_query = [f"&metric_list={i}" for i in metrics_query]
        query_text = f'?ids={self.ids[0]}&ids={self.ids[1]}' + "".join(metrics_query)
        comparison_table_url = reverse('Comparison table')
        response = self.client.get(comparison_table_url + query_text)
        # Check the table is correctly provided and has expected length
        assert response.status_code == 200

    def test_get_comparison_plots_for_metric(self):
        plots_comparison_url = reverse('Comparison plots')

        # try out several configurations with only plots for 'R'
        # Should work normally and return one plot, as default 'get_intersection=false'
        # and a mapplot cannot be produced of the total extent
        response = self.client.get(
            plots_comparison_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                   f'metric=R&'
                                   f'plot_types=boxplot&plot_types=mapplot'
        )
        # Should work normally and return two plots (intersection only)
        response_intersection = self.client.get(
            plots_comparison_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                   f'metric=R&'
                                   f'get_intersection=true&'
                                   f'plot_types=boxplot&plot_types=mapplot'
        )
        # Should work normally and return one plot (boxplot)
        # only - mapplot different cannot be generated here
        response_non_overl_extent = self.client.get(
            plots_comparison_url + f'?ids={self.ids[0]}&ids={self.ids[2]}&'
                                   f'metric=R&'
                                   f'get_intersection=false&'
                                   f'plot_types=boxplot&plot_types=mapplot'
        )

        assert response.status_code == 200
        assert list(response.json()[0].keys()) == ['plot']
        assert response_intersection.status_code == 200
        assert list(response.json()[0].keys()) == ['plot']
        assert response_non_overl_extent.status_code == 200
        assert list(response.json()[0].keys()) == ['plot']

    def test_get_spatial_extent(self):
        spatial_extent_url = reverse('Extent image')

        response = self.client.get(
            spatial_extent_url + f'?ids={self.ids[0]}&ids={self.ids[1]}'
        )
        response_intersection = self.client.get(
            spatial_extent_url + f'?ids={self.ids[0]}&ids={self.ids[1]}&'
                                 f'get_intersection=true'
        )
        response_non_overl_extent = self.client.get(
            spatial_extent_url + f'?ids={self.ids[0]}&ids={self.ids[2]}&'
                                 f'get_intersection=false&'
        )
        assert response.status_code == 200
        assert response_intersection.status_code == 200
        assert response_non_overl_extent.status_code == 200

    def test_get_validations_for_comparison(self):
        val4comparison_url = reverse('Get validations for comparison')

        response = self.client.get(val4comparison_url + f'?max_datasets=1&'
                                                        f'ref_version=ISMN_V20180712_MINI')
        # test response null with two non-ref datasets and
        # with wrong ref dataset version
        response_n_datasets = self.client.get(val4comparison_url + f'?max_datasets=2&'
                                                                   f'ref_version=ISMN_V20180712_MINI')
        response_wongref = self.client.get(val4comparison_url + f'?max_datasets=2&'
                                                                f'ref_version=ISMN_V20191211')

        assert response.status_code == 200
        assert response_n_datasets.status_code == 200
        assert response_wongref.status_code == 200
        # meaning no validations were found with the given settings
        assert response_n_datasets.get("Content-Length") == "4"
        assert response_wongref.get("Content-Length") == "4"

    def doCleanups(self):
        # Clean up the validation directories used for testing
        delete_run(self.run)
        delete_run(self.run_partially_overlapping)
        delete_run(self.run_non_overlapping)
