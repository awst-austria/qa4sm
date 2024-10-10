import logging
import time

from django.urls import reverse

from django.test.testcases import TransactionTestCase
from rest_framework.test import APIClient

from api.tests.test_helper import *
from validator.validation import globals
from django.test.utils import override_settings

User = get_user_model()


class TestValidationConfigView(TransactionTestCase):
    # This re-inits the database for every test, see
    # https://docs.djangoproject.com/en/2.0/topics/testing/overview/#test-case-serialized-rollback
    # It's necessary because the validation view closes the db connection
    # and then the following tests complain about the closed connection.
    # Apparently, re-initing the db creates a new connection every time, so
    # problem solved.
    serialized_rollback = True

    ## https://docs.djangoproject.com/en/2.2/topics/testing/tools/#simpletestcase
    databases = '__all__'
    allow_database_queries = True

    __logger = logging.getLogger(__name__)

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'networks', 'users']

    def setUp(self):
        # creating the main user to run a validation
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.alt_data, self.alt_test_user = create_alternative_user()
        # I need to run this validation to check if there exists one
        self.run = create_default_validation_without_running(self.test_user)
        self.run.save()
        # self.run_id = self.run.id
        self.wrong_id = 'f0000000-a000-b000-c000-d00000000000'

        basic_filter_id = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id
        self.good_form = {'dataset_configs': [{'dataset_id': Dataset.objects.get(short_name=globals.C3SC).id,
                                               'variable_id': DataVariable.objects.get(pretty_name=globals.C3S_sm).id,
                                               'version_id': DatasetVersion.objects.get(
                                                   short_name=globals.C3S_V201812).id,
                                               'basic_filters': [basic_filter_id],
                                               'parametrised_filters': [],
                                               'is_spatial_reference': False,
                                               'is_temporal_reference': False,
                                               'is_scaling_reference': False},
                                              {'dataset_id': Dataset.objects.get(short_name=globals.SMAP_L3).id,
                                               'variable_id': DataVariable.objects.get(
                                                   pretty_name=globals.SMAP_soil_moisture).id,
                                               'version_id': DatasetVersion.objects.get(
                                                   short_name=globals.SMAP_V6_PM).id,
                                               'basic_filters': [basic_filter_id],
                                               'parametrised_filters': [],
                                               'is_spatial_reference': False,
                                               'is_temporal_reference': False,
                                               'is_scaling_reference': False},
                                              {'dataset_id': Dataset.objects.get(short_name=globals.GLDAS).id,
                                               'variable_id': DataVariable.objects.get(
                                                   pretty_name=globals.GLDAS_SoilMoi0_10cm_inst).id,
                                               'version_id': DatasetVersion.objects.get(
                                                   short_name=globals.GLDAS_NOAH025_3H_2_1).id,
                                               'basic_filters': [basic_filter_id],
                                               'parametrised_filters': [],
                                               'is_spatial_reference': True,
                                               'is_temporal_reference': True,
                                               'is_scaling_reference': False}],
                          'interval_from': datetime(1978, 1, 1),
                          'interval_to': datetime(2020, 1, 1),
                          'min_lat': 18.022843268729,
                          'min_lon': -161.334244440612,
                          'max_lat': 23.0954743716834,
                          'max_lon': -153.802918037877,
                          'metrics': [{'id': 'tcol', 'value': True}],
                          'anomalies_method': 'none',
                          'anomalies_from': None,
                          'anomalies_to': None,
                          'scaling_method': ValidationRun.NO_SCALING,
                          'name_tag': 'test_validation',
                          'temporal_matching': globals.TEMP_MATCH_WINDOW,
                          'intra_annual_metrics': {
                              'intra_annual_metrics': False,
                              'intra_annual_type': '',
                              'intra_annual_overlap': None
                          }}

    def test_start_validation(self):
        start_validation_url = reverse('Run new validation')
        good_form = self.good_form.copy()

        # not logged in client:
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 403
        assert response.json()['detail'] == 'Authentication credentials were not provided.'

        # log in
        self.client.login(**self.auth_data)

        # submit without checking for an existing validation
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 200
        assert len(ValidationRun.objects.all()) == 2  # now should be 2, the one from the setup and this one

        # here I'll submit a validation that already exists and at the same time I'll check parameterised filters
        # to do that I have to wait for adding parameterised filters to the view
        # existing_val_form = {'dataset_configs': [{'dataset_id': Dataset.objects.get(short_name=globals.C3S).id,
        #                                   'variable_id': DataVariable.objects.get(short_name=globals.C3S_sm).id,
        #                                   'version_id': DatasetVersion.objects.get(short_name=globals.C3S_V202012).id,
        #                                   'basic_filters': [basic_filter_id, DataFilter.objects.get(name='FIL_C3S_FLAG_0').id],
        #                                   'parametrised_filters': []}],
        #             'reference_config': {'dataset_id': Dataset.objects.get(short_name=globals.ISMN).id,
        #                                  'variable_id': DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id,
        #                                  'version_id': DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id,
        #                                  'basic_filters': [DataFilter.objects.get(name='FIL_ISMN_GOOD').id],
        #                                  'parametrised_filters': []},
        #              'interval_from': datetime(1978, 1, 1, tzinfo=UTC),
        #              'interval_to': datetime(2018, 12, 31, tzinfo=UTC),
        #              'min_lat': 18.022843268729,
        #              'min_lon': -161.334244440612,
        #              'max_lat': 23.0954743716834,
        #              'max_lon': -153.802918037877,
        #              'metrics': [{'id': 'tcol', 'value': True}],
        #              'anomalies_method': ValidationRun.CLIMATOLOGY,
        #              'anomalies_from': datetime(1990, 1, 1, 0, 0, tzinfo=UTC),
        #              'anomalies_to': datetime(2010, 12, 31, 23, 59, 59, tzinfo=UTC),
        #              'scaling_method': ValidationRun.NO_SCALING,
        #              'name_tag': 'test_validation'}

        # response = self.client.post(start_validation_url, existing_val_form, format='json')
        # assert response.status_code == 200

        empty_form = {'dataset_configs': '',
                      'interval_from': '',
                      'interval_to': '',
                      'min_lat': '',
                      'min_lon': '',
                      'max_lat': '',
                      'max_lon': '',
                      'metrics': '',
                      'anomalies_method': 'none',
                      'anomalies_from': '',
                      'anomalies_to': '',
                      'scaling_method': '',
                      'name_tag': '',
                      'temporal_matching': ''
                      }

        response = self.client.post(start_validation_url, empty_form, format='json')
        assert response.status_code == 400

        # changing reference settings:
        # setting method different from none and not indicating any data config as scaling ref
        good_form['scaling_method'] = ValidationRun.MEAN_STD
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # fixing the above problem by indicating scaling ref
        good_form['dataset_configs'][2]['is_scaling_reference'] = True
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 200

        # setting more than one config as reference
        # spatial:
        good_form['dataset_configs'][0]['is_spatial_reference'] = True
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # temporal:
        good_form['dataset_configs'][0]['is_spatial_reference'] = False  # fixing this one
        good_form['dataset_configs'][0]['is_temporal_reference'] = True
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # scaling
        good_form['dataset_configs'][0]['is_temporal_reference'] = False  # fixing this one
        good_form['dataset_configs'][0]['is_scaling_reference'] = True
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # setting no configs as reference:
        # spatial
        good_form['dataset_configs'][2]['is_spatial_reference'] = False
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # temporal
        good_form['dataset_configs'][2]['is_spatial_reference'] = True  # fixing this one
        good_form['dataset_configs'][2]['is_temporal_reference'] = False
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # scaling
        good_form['dataset_configs'][2]['is_temporal_reference'] = True  # fixing this one
        good_form['dataset_configs'][0]['is_scaling_reference'] = False
        good_form['dataset_configs'][2]['is_scaling_reference'] = False

        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

        # setting no scaling to fix the form
        good_form['scaling_method'] = ValidationRun.NO_SCALING

        # removing some fields and posting not full form
        del good_form['max_lon']  # not relevant, it can be null
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 200

        del good_form['dataset_configs']  # relevant, can not be omitted
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 400

    def test_get_validation_configuration(self):
        validation_configuration_url = reverse('Validation configuration', kwargs={'id': self.run.id})

        # existing validation - check if everything is read properly
        response = self.client.get(validation_configuration_url)
        val_run_dict = response.json()
        assert response.status_code == 200
        assert val_run_dict['name_tag'] == ''
        assert val_run_dict['interval_from'] == '1978-01-01'
        assert val_run_dict['interval_to'] == '2018-12-31'
        assert val_run_dict['anomalies_method'] == 'climatology'
        assert val_run_dict['anomalies_from'] == '1990-01-01'
        assert val_run_dict['anomalies_to'] == '2010-12-31'
        assert val_run_dict['min_lat'] is None
        assert val_run_dict['min_lon'] is None
        assert val_run_dict['max_lat'] is None
        assert val_run_dict['max_lon'] is None
        assert val_run_dict['scaling_method'] == 'none'
        assert not val_run_dict['metrics'][0]['value']
        assert val_run_dict['dataset_configs'][0]['dataset_id'] == Dataset.objects.get(short_name=globals.C3SC).id
        assert val_run_dict['dataset_configs'][0]['version_id'] == \
               DatasetVersion.objects.get(short_name=globals.C3S_V202012).id
        assert val_run_dict['dataset_configs'][0]['variable_id'] == \
               DataVariable.objects.get(pretty_name=globals.C3S_sm).id
        assert val_run_dict['dataset_configs'][0]['is_spatial_reference'] is False
        assert val_run_dict['dataset_configs'][0]['is_temporal_reference'] is False
        assert val_run_dict['dataset_configs'][0]['is_scaling_reference'] is False
        assert val_run_dict['temporal_matching'] == globals.TEMP_MATCH_WINDOW
        #  applied all existing settings, so there will be no change
        assert 'changes' not in val_run_dict.keys()

        # non existing validation - 404 expected
        response = self.client.get(reverse('Validation configuration', kwargs={'id': self.wrong_id}))
        assert response.status_code == 404

    # stopping validation tested here, because TransactionTestCase is needed and using it in two places causes some
    # issues
    def test_stop_validation(self):
        # start a new validation (tcol is run here, because a default one would finish before I cancel it :) )
        start_validation_url = reverse('Run new validation')

        basic_filter_id = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id
        good_form = self.good_form.copy()

        # log in
        self.client.login(**self.auth_data)

        # submit without checking for an existing validation
        response = self.client.post(start_validation_url, good_form, format='json')
        run_id = response.json()['id']
        self.assertEqual(response.status_code, 200)

        # # let it run a little
        time.sleep(1)
        # # the validation has just started so the progress must be below 100
        new_run = ValidationRun.objects.get(pk=run_id)

        assert new_run.progress < 100
        # now let's try out cancelling the validation
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 200
        #
        # let's try canceling non-existing validation
        response = self.client.delete(
            reverse('Stop validation', kwargs={'result_uuid': 'f0000000-a000-b000-c000-d00000000000'}))
        assert response.status_code == 404

        # let's try to submit wrong method
        response = self.client.get(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 405

        # log out and check the access
        self.client.logout()
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 403

        # log in as another user and check the access
        self.client.login(**self.alt_data)
        response = self.client.delete(reverse('Stop validation', kwargs={'result_uuid': new_run.id}))
        assert response.status_code == 403

        # give it some time
        time.sleep(5)
        # the progress should be -1, but it takes some time for a validation to settle down so setting -1 here would
        # require some time, but we can check that it's not bigger than 0 so there was no progress
        assert new_run.progress <= 0
