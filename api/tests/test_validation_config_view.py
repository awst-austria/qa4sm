import logging
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

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'networks']

    def setUp(self):
        # creating the main user to run a validation
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()

        # I need to run this validation to check if there exists one
        self.run = create_default_validation_without_running(self.test_user)
        self.run.save()
        # self.run_id = self.run.id
        self.wrong_id = 'f0000000-a000-b000-c000-d00000000000'

    def test_start_validation(self):
        start_validation_url = reverse('Run new validation')

        basic_filter_id = DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id
        good_form = {'dataset_configs': [{'dataset_id': Dataset.objects.get(short_name=globals.C3S).id,
                                          'variable_id': DataVariable.objects.get(short_name=globals.C3S_sm).id,
                                          'version_id': DatasetVersion.objects.get(short_name=globals.C3S_V201812).id,
                                          'basic_filters': [basic_filter_id],
                                          'parametrised_filters': []},
                                         {'dataset_id': Dataset.objects.get(short_name=globals.SMAP).id,
                                          'variable_id': DataVariable.objects.get(
                                              short_name=globals.SMAP_soil_moisture).id,
                                          'version_id': DatasetVersion.objects.get(short_name=globals.SMAP_V6_PM).id,
                                          'basic_filters': [basic_filter_id],
                                          'parametrised_filters': []}],
                     'reference_config': {'dataset_id': Dataset.objects.get(short_name=globals.GLDAS).id,
                                          'variable_id': DataVariable.objects.get(
                                              short_name=globals.GLDAS_SoilMoi0_10cm_inst).id,
                                          'version_id': DatasetVersion.objects.get(
                                              short_name=globals.GLDAS_NOAH025_3H_2_1).id,
                                          'basic_filters': [basic_filter_id],
                                          'parametrised_filters': []},
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
                     'scaling_method': ValidationRun.MEAN_STD,
                     'scale_to': ValidationRun.SCALE_TO_REF,
                     'name_tag': 'test_validation'}

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
        #              'scale_to': 'ref',
        #              'name_tag': 'test_validation'}

        # response = self.client.post(start_validation_url, existing_val_form, format='json')
        # assert response.status_code == 200

        empty_form = {'dataset_configs': '',
                      'reference_config': '',
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
                      'scale_to': '',
                      'name_tag': ''
                      }

        response = self.client.post(start_validation_url, empty_form, format='json')
        assert response.status_code == 400

        # removing some fields and posting not full form

        del good_form['max_lon'] # not relevant, it can be null
        response = self.client.post(start_validation_url, good_form, format='json')
        assert response.status_code == 200

        del good_form['dataset_configs'] # relevant, can not be omitted
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
        assert val_run_dict['reference_config']['dataset_id'] == \
               Dataset.objects.get(short_name=globals.ISMN).id
        assert val_run_dict['reference_config']['version_id'] == \
               DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id
        assert val_run_dict['reference_config']['variable_id'] ==\
               DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id
        assert DataFilter.objects.get(name='FIL_ISMN_GOOD').id in val_run_dict['reference_config']['basic_filters']

        param_filters_id = [p_filter.filter_id for p_filter in
                            ParametrisedFilter.objects.filter(dataset_config=self.run.reference_configuration)]

        assert param_filters_id == [el['id'] for el in val_run_dict['reference_config']['parametrised_filters']]
        assert DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id in \
               val_run_dict['dataset_configs'][0]['basic_filters']

        assert val_run_dict['dataset_configs'][0]['dataset_id'] == Dataset.objects.get(short_name=globals.C3S).id
        assert val_run_dict['dataset_configs'][0]['version_id'] == \
               DatasetVersion.objects.get(short_name=globals.C3S_V202012).id
        assert val_run_dict['dataset_configs'][0]['variable_id'] == \
               DataVariable.objects.get(short_name=globals.C3S_sm).id

        # non existing validation - 404 expected
        response = self.client.get(reverse('Validation configuration', kwargs={'id': self.wrong_id}))
        assert response.status_code == 404

