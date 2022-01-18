import logging

from django.urls import reverse
from django.test import tag

from django.test import TestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *
from api.views.comparison_view import *

import validator.validation as val


class TestValidationComparisonView(TestCase):
    # Test all functions in api/views/comparison_view.py
    __logger = logging.getLogger(__name__)
    fixtures = ['datasets', 'filters', 'versions', 'variables']

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

    @tag('slow')
    def test_get_validations(self):
        ids = [self.run.id, self.run_partially_overlapping.id]
        runs = get_validations(ids=ids)

        assert len(runs) == 2
        assert runs[0].name_tag == 'initial validation'
        assert runs[1].name_tag == 'partially overlapping'

    @tag('slow')
    def test_get_comparison_table(self):
        ids = [str(i) for i in (self.run.id, self.run_partially_overlapping.id)]
        comparison_table_url = reverse('Comparison table')

        # try out several configurations
        response = self.client.get(
            comparison_table_url + f'?ids={ids[0]}&ids={ids[1]}&metric_list=R&metric_list=urmsd'
        )
        response_intersection = self.client.get(
            comparison_table_url + f'?ids={ids[0]}&ids={ids[1]}&metric_list=R&metric_list=urmsd&get_intersection=true'
        )
        # TODO: how to pass extent?
        # response_wrong_extent = self.client.get(
        #     comparison_table_url + f'?ids={ids[0]}&ids={ids[1]}'
        #                            f'&metric_list=R&metric_list=urmsd'
        #                            f'&get_intersection=true'
        #                            f'&extent=(0,0,0,0)'
        # )

        assert response.status_code == 200
        assert response_intersection.status_code == 200

        # TODO: this should fail and return a string response (status 200)
        # assert response_wrong_extent.status_code == 200
        # assert response_wrong_extent.json() ...

    @tag('slow')
    def test_download_comparison_table(self):
        ids = [str(i) for i in (self.run.id, self.run_partially_overlapping.id)]
        down_comparison_table_url = reverse('Download comparison csv')

        response = self.client.get(
            down_comparison_table_url + f'?ids={ids[0]}&ids={ids[1]}&metric_list=R&metric_list=urmsd'
        )

        assert response.status_code == 200
        assert 'Comparison_summary.csv' in response.get('Content-Disposition')

    @tag('slow')
    def test_get_comparison_metrics(self):
        ids = [str(i) for i in (self.run.id, self.run_partially_overlapping.id)]
        metric_comparison_url = reverse('Comparison metrics')

        # try out several configurations
        response = self.client.get(
            metric_comparison_url + f'?ids={ids[0]}&ids={ids[1]}'
        )
        response_intersection = self.client.get(
            metric_comparison_url + f'?ids={ids[0]}&ids={ids[1]}&get_intersection=true'
        )

        assert response.status_code == 200
        assert response_intersection.status_code == 200

        metric_list = response_intersection.json()
        assert len(metric_list) == 12
        for metric in metric_list:
            assert 'metric_pretty_name' in metric.keys()
            assert 'metric_query_name' in metric.keys()

    # @tag('slow')
    # def test_get_comparison_plots_for_metric(self):
    #
    #
    # @tag('slow')
    # def test_get_spatial_extent(self):
    #     id1 = str(self.run.id)
    #     spatial_extent_url = reverse('Extent image')

    def doCleanups(self):
        # Clean up the validation directories used for testing
        delete_run(self.run)
        delete_run(self.run_partially_overlapping)
        delete_run(self.run_non_overlapping)
