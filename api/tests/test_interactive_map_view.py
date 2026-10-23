from rest_framework.test import APIClient
from django.test.testcases import TransactionTestCase
from rest_framework.test import APIClient
from api.tests.test_helper import *
import api.views.interactive_map_view as view
import pytest
from django.conf import settings
from unittest.mock import patch
from django.test import RequestFactory
import xarray as xr
import json


def create_default_validation_without_running_including_zarr(user, tcol=False):
    run = default_parameterized_validation_to_be_run(user, tcol)
    run.zarr_path = r'/testdata/output_data/c3s_ismn.zarr'
    run.save()
    return run


TEST_ZARR_PATH = os.path.join(settings.BASE_DIR, 'testdata', 'output_data',
                              'c3s_ismn.zarr')


@patch('api.views.interactive_map_view.get_cached_zarr_path')
@patch('api.views.interactive_map_utils.get_cached_zarr_dataset')
@patch('api.services.interactive_map_service.get_cached_zarr_path')
class TestZarrFunctions(TransactionTestCase):
    serialized_rollback = True
    databases = '__all__'
    allow_database_queries = True
    fixtures = [
        'variables', 'versions', 'datasets', 'filters', 'networks', 'users'
    ]

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()

        self.run = create_default_validation_without_running_including_zarr(
            self.test_user)
        self.factory = RequestFactory()
        self.validation_id = str(self.run.id)
        self.layer_name = 'mse_between_0-ISMN_and_1-C3S_combined'
        self.metric_name = 'mse'

        # Load test dataset here with consolidated=False
        self.test_dataset = xr.open_zarr(TEST_ZARR_PATH, consolidated=False)

    def test_get_data_point(self, mock_get_zarr_path, mock_get_zarr_dataset,
                            mock_get_zarr_path_view):
        """Test get_data_point with valid coordinates."""
        mock_get_zarr_path.return_value = TEST_ZARR_PATH
        mock_get_zarr_dataset.return_value = self.test_dataset

        request = self.factory.get(
            f'/api/validation/{self.validation_id}/metric/{self.metric_name}/layer/{self.layer_name}/point/',
            {
                'x': -155.33048916660033,
                'y': 19.794560119976104,
                'z': 9.66024552136863,
                'projection': 4326
            })

        response = view.get_data_point(request, self.validation_id,
                                       self.metric_name, self.layer_name)
        assert response.status_code == 200

        data = json.loads(response.content)

        # Assert response structure
        assert 'candidates' in data
        assert 'multiple_found' in data
        assert 'source' in data
        assert 'is_ismn' in data

        # Assert specific values
        assert data['source'] == 'ismn'
        assert data['is_ismn'] is True
        assert data['multiple_found'] is False

        # Assert candidate data
        assert len(data['candidates']) == 1
        candidate = data['candidates'][0]
        assert candidate['station'] == 'PuaAkala'
        assert candidate['network'] == 'SCAN'
        assert 'lat' in candidate
        assert 'lon' in candidate

        x = 0
        y = 0
        z = 6

        request2 = self.factory.get(
            f'/api/validation/{self.validation_id}/metric/{self.metric_name}/layer/{self.layer_name}/point/',
            {
                'x': x,
                'y': y,
                'z': z,
                'projection': 3857
            })

        response2 = view.get_data_point(request2, self.validation_id,
                                        self.metric_name, self.layer_name)
        assert response2.status_code == 404
        data2 = json.loads(response2.content)

        assert 'error' in data2
        assert data2['error'] == 'No data found at this location'

    def test_metadata(self, mock_get_zarr_path, mock_get_zarr_dataset,
                      mock_get_zarr_path_view):
        """Test metadata with valid coordinates."""
        mock_get_zarr_path_view.return_value = TEST_ZARR_PATH
        mock_get_zarr_dataset.return_value = self.test_dataset

        possible_layers = {
            'n_obs': ['n_obs'],
            'status': ['status_between_0-ISMN_and_1-C3S_combined'],
            'RSS': ['RSS_between_0-ISMN_and_1-C3S_combined'],
            'rho': ['rho_between_0-ISMN_and_1-C3S_combined'],
            'BIAS': ['BIAS_between_0-ISMN_and_1-C3S_combined'],
            'p_rho': ['p_rho_between_0-ISMN_and_1-C3S_combined'],
            'urmsd': ['urmsd_between_0-ISMN_and_1-C3S_combined'],
            'mse_corr': ['mse_corr_between_0-ISMN_and_1-C3S_combined'],
            'mse_bias': ['mse_bias_between_0-ISMN_and_1-C3S_combined'],
            'mse_var': ['mse_var_between_0-ISMN_and_1-C3S_combined'],
            'R': ['R_between_0-ISMN_and_1-C3S_combined'],
            'p_R': ['p_R_between_0-ISMN_and_1-C3S_combined'],
            'RMSD': ['RMSD_between_0-ISMN_and_1-C3S_combined'],
            'mse': ['mse_between_0-ISMN_and_1-C3S_combined']
        }

        request = self.factory.post(
            f'/api/validation/{self.validation_id}/metadata/',
            data=json.dumps({'possible_layers': possible_layers}),
            content_type='application/json')

        response = view.get_validation_layer_metadata(request,
                                                      self.validation_id)

        # Assert status code
        self.assertEqual(response.status_code, 200)

        # Parse response content
        data = json.loads(response.content)

        # Assert validation_id exists
        self.assertIn('validation_id', data)

        # Assert layers is a list with 14 elements
        self.assertEqual(len(data['layers']), 14)

        # Assert first layer has correct name and metric
        self.assertEqual(data['layers'][0]['name'], 'n_obs')
        self.assertEqual(data['layers'][0]['metric'], 'n_obs')

        # Assert status layer is categorical
        status_layer = data['layers'][1]
        self.assertTrue(status_layer['colormap']['is_categorical'])

        # Assert unit structure
        self.assertEqual(data['unit']['common_unit'], 'm³/m³')
        self.assertFalse(data['unit']['from_scaling_ref'])

        # Assert status_metadata exists and has entries
        self.assertIn('status_metadata', data)
        status_key = list(data['status_metadata'].keys())[0]
        self.assertIn('entries', data['status_metadata'][status_key])

    def test_layer_bounds(self, mock_get_zarr_path, mock_get_zarr_dataset,
                          mock_get_zarr_path_view):
        """Test metadata with valid coordinates."""
        mock_get_zarr_path_view.return_value = TEST_ZARR_PATH
        mock_get_zarr_dataset.return_value = self.test_dataset

        request = self.factory.get(
            f'/api/validation/{self.validation_id}/bounds/')

        response = view.get_layer_bounds(request, self.validation_id)
        # Assert status code
        self.assertEqual(response.status_code, 200)

        # Parse respons
        data = json.loads(response.content)

        # Assert values
        expected_extent = [-155.9351131, 19.5275972, -155.3258569, 20.1011228]
        expected_center = [-155.630485, 19.81436]

        for i, val in enumerate(expected_extent):
            self.assertAlmostEqual(data['extent'][i], val, places=5)
        for i, val in enumerate(expected_center):
            self.assertAlmostEqual(data['center'][i], val, places=5)
        self.assertEqual(data['num_points'], 25)

    def test_get_layer_range(self, mock_get_zarr_path, mock_get_zarr_dataset,
                             mock_get_zarr_path_view):
        """Test get_layer_range endpoint."""
        mock_get_zarr_path.return_value = TEST_ZARR_PATH
        mock_get_zarr_path_view.return_value = TEST_ZARR_PATH
        mock_get_zarr_dataset.return_value = self.test_dataset

        request = self.factory.get(
            f'/api/validation/{self.validation_id}/range/{self.metric_name}/{self.layer_name}/'
        )

        response = view.get_layer_range(request, self.validation_id,
                                        self.metric_name, self.layer_name)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['vmin'] == 0.0
        assert data['vmax'] == pytest.approx(0.045760247856378555, rel=1e-6)
        assert data['is_categorical'] is False
        assert data['has_constraints'] is True

    def test_get_tile(self, mock_get_zarr_path, mock_get_zarr_dataset,
                      mock_get_zarr_path_view):
        """Test get_tile endpoint."""
        mock_get_zarr_path.return_value = TEST_ZARR_PATH
        mock_get_zarr_path_view.return_value = TEST_ZARR_PATH
        mock_get_zarr_dataset.return_value = self.test_dataset

        x = 137
        y = 397
        z = 10
        projection = 4326

        request = self.factory.get(
            f'/api/validation/{self.validation_id}/tiles/{self.metric_name}/{self.layer_name}/{projection}/{z}/{x}/{y}.png'
        )

        response = view.get_tile(request, self.validation_id, self.metric_name,
                                 self.layer_name, projection, z, x, y)

        assert response.status_code == 200
        assert response['Content-Type'] == 'image/png'
