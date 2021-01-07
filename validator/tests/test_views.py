from datetime import datetime, timedelta
import io
import json
import logging
from re import findall as regex_find
from time import sleep
import time
import zipfile

from dateutil import parser
from dateutil.tz import tzlocal
from django.contrib.auth import get_user_model
from validator.forms import PublishingForm

User = get_user_model()

from django.core import mail
from django.test.testcases import TransactionTestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.conf import settings
import pytest
from pytz import UTC
from pytz import utc

from validator.forms.user_profile import UserProfileForm
from validator.models import ValidationRun
from validator.models.dataset import Dataset
from validator.models.filter import DataFilter
from validator.models.settings import Settings
from validator.models.variable import DataVariable
from validator.models.version import DatasetVersion
from validator.urls import urlpatterns
from validator.validation import globals
from os import path
import shutil
from validator.validation.globals import OUTPUT_FOLDER
from validator.validation import set_outfile, mkdir_if_not_exists

from django.utils.http import urlencode
import os

class TestViews(TransactionTestCase):
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
        self.__logger = logging.getLogger(__name__)

        settings = Settings.load()
        settings.maintenance_mode = False
        settings.save()

        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}

        # second test user
        self.credentials2 = {
            'username': 'seconduser',
            'password': 'shush!',
            'email': 'forgetful@test.com'}

        try:
            self.testuser = User.objects.get(username=self.credentials['username'])
            self.testuser2 = User.objects.get(username=self.credentials2['username'])
        except User.DoesNotExist:
            self.testuser = User.objects.create_user(**self.credentials)
            self.testuser2 = User.objects.create_user(**self.credentials2)

        run_params = {
            'id': '67fc185b-5cd7-4caa-83f0-983e605ede5f',
            'user': self.testuser,
            'start_time': datetime.utcnow().replace(tzinfo=utc) - timedelta(hours=1),
            'end_time': datetime.utcnow().replace(tzinfo=utc),
            'total_points': 30,
            'error_points': 5,
        }
        ## Create a test validation run with a specific id so that it can
        ## be accessed via a URL containing that id
        self.testrun = ValidationRun.objects.create(**run_params)
        ## make sure the run's output file name is set:
        self.testrun.output_file.name = str(self.testrun.id) + '/foobar.nc'
        self.testrun.save()

        self.public_views = ['login', 'logout', 'home', 'published_results', 'signup', 'signup_complete', 'terms',
                             'datasets', 'alpha', 'help', 'about', 'password_reset', 'password_reset_done',
                             'password_reset_complete', 'user_profile_deactivated']
        self.parameter_views = ['result', 'ajax_get_dataset_options', 'ajax_get_version_id', 'password_reset_confirm', 'stop_validation']
        self.private_views = [p.name for p in urlpatterns if hasattr(p,
                                                                     'name') and p.name is not None and p.name not in self.public_views and p.name not in self.parameter_views]

    ## Ensure that anonymous access is prevented for private pages
    def test_views_deny_anonymous(self):
        login_url = reverse('login')
        testurls = [reverse(tv) for tv in self.private_views]

        for url in testurls:
            self.__logger.info(url)
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, '{}?next={}'.format(login_url, url), msg_prefix=url)
            response = self.client.post(url, follow=True)
            self.assertRedirects(response, '{}?next={}'.format(login_url, url), msg_prefix=url)

    ## Check that with valid credentials (set in setUp), access is possible
    def test_views_login(self):
        testurls = [reverse(tv) for tv in self.private_views]

        for url in testurls:
            self.client.login(**self.credentials)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    ## Check that the publicly available views are publicly available anonymously
    def test_public_views(self):
        for pv in self.public_views:
            url = reverse(pv)
            self.__logger.debug("Testing {}".format(url))
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    ## Check the results view (with parameter URL)
    def test_result_view(self):
        url = reverse('result', kwargs={'result_uuid': self.testrun.id})
        self.client.login(**self.credentials)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_result_expiry(self):
        url = reverse('result', kwargs={'result_uuid': self.testrun.id})

        ## only owners should be able to change validations
        self.client.login(**self.credentials2)
        # response = self.client.patch(url, 'extend=true', content_type='application/x-www-form-urlencoded;')
        response = self.client.patch(url, 'extend=true', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 403)

        ## try out normal expiry extension
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'extend=true', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 200)
        new_expiry_date = parser.parse(response.content)
        self.assertTrue(new_expiry_date is not None)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date == new_expiry_date

        ## invalid expiry extension
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'extend=false', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 400)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date == new_expiry_date

        ## valid archiving
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'archive=true', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 200)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date is None

        ## valid un-archiving
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'archive=false', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 200)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date is not None

        ## invalid archiving
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'archive=asdf', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 400)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date is not None

        ## completely invalid parameter
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'levelup=1up', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 400)
        assert ValidationRun.objects.get(pk=self.testrun.id).expiry_date is not None

    @pytest.mark.skipif(not 'DOI_ACCESS_TOKEN_ENV' in os.environ, reason="No access token set in global variables")
    @override_settings(DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions")
    def test_result_publishing(self):
        infile = 'testdata/output_data/c3s_era5land.nc'

        url = reverse('result', kwargs={'result_uuid': self.testrun.id})

        # use the publishing form to convert the validation metadata to a dict
        metadata = PublishingForm()._formdata_from_validation(self.testrun)

        ## only owners should be able to change validations
        self.client.login(**self.credentials2)
        response = self.client.patch(url, urlencode(metadata))
        self.assertEqual(response.status_code, 403)

        self.client.login(**self.credentials)

        # shouldn't work because of incorrect parameter
        metadata['publish'] = 'asdf'
        response = self.client.patch(url, urlencode(metadata))
        self.__logger.debug("{} {}".format(response.status_code, response.content))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.content is not None)

        metadata['publish'] = 'true'

        # shouldn't work because input metadata is not valid
        orig_orcid = metadata['orcid']
        metadata['orcid'] = 'this is no orcid'
        orig_keywords = metadata['keywords']
        metadata['keywords'] = metadata['keywords'].replace('qa4sm', '')
        response = self.client.patch(url, urlencode(metadata))
        self.__logger.debug("{} {}".format(response.status_code, response.content))
        self.assertEqual(response.status_code, 420)
        self.assertTrue(response.content is not None)

        metadata['orcid'] = orig_orcid
        metadata['keywords'] = orig_keywords

        # remove file path from validation
        self.testrun.output_file = None
        self.testrun.save()
        self.testrun = ValidationRun.objects.get(pk=self.testrun.id)  # reload

        # shouldn't work because of missing file path in validation
        response = self.client.patch(url, urlencode(metadata))
        self.__logger.debug("{} {}".format(response.status_code, response.content))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.content is not None)

        ## set valid output file for validation
        run_dir = path.join(OUTPUT_FOLDER, str(self.testrun.id))
        mkdir_if_not_exists(run_dir)
        shutil.copy(infile, path.join(run_dir, 'results.nc'))
        set_outfile(self.testrun, run_dir)
        self.testrun.save()
        self.testrun = ValidationRun.objects.get(pk=self.testrun.id)  # reload

        ## simulate that publishing is already in progress
        self.testrun.publishing_in_progress = True
        self.testrun.save()
        self.testrun = ValidationRun.objects.get(pk=self.testrun.id)  # reload
        response = self.client.patch(url, urlencode(metadata))
        self.__logger.debug("{} {}".format(response.status_code, response.content))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.content is not None)

        ## remove in progress flag
        self.testrun.publishing_in_progress = False
        self.testrun.save()

        # should work now
        response = self.client.patch(url, urlencode(metadata))
        self.__logger.debug("{} {}".format(response.status_code, response.content))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content is not None)

    def test_delete_result(self):
        # create result to delete:
        run = ValidationRun()
        run.user = self.testuser
        run.start_time = datetime.now(tzlocal())
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
        run.save()
        result_id = str(run.id)

        assert result_id, "Error saving the test validation run."

        url = reverse('result', kwargs={'result_uuid': result_id})

        # try deleting other user's result - should be blocked
        self.client.login(**self.credentials2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # log in as owner of result
        self.client.login(**self.credentials)

        # try deleting a result that already has a DOI, should be blocked
        run.doi = '10.1000/182'
        run.save()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

        # remove DOI again
        run.doi = ''
        run.save()

        # try to delete own result, should succeed
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

        assert not ValidationRun.objects.filter(pk=result_id).exists(), "Validation run didn't get deleted."

    def test_change_validation_name(self):
        # create new no-named result
        run = ValidationRun()
        run.user = self.testuser
        run.start_time = datetime.now(tzlocal())
        run.interval_from = datetime(1978, 1, 1, tzinfo=UTC)
        run.interval_to = datetime(2018, 1, 1, tzinfo=UTC)
        run.save()
        result_id = str(run.id)

        assert result_id, "Error saving the test validation run."

        #try to change name of other user's validation
        url = reverse('result', kwargs={'result_uuid': result_id})

        self.client.login(**self.credentials2)
        response = self.client.patch(url, 'save_name=false', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 403)

        # log in as owner of result and check invalid saving mode
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'save_name=false', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 400)

        # log in as owner of result and check valid saving mode
        self.client.login(**self.credentials)
        response = self.client.patch(url, 'save_name=true&new_name="new_name"', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 200)

        run.doi = '10.1000/182'
        run.save()

        response = self.client.patch(url, 'save_name=true&new_name="new_name"', content_type='application/x-www-form-urlencoded;')
        self.assertEqual(response.status_code, 405)

        run.doi = ''
        run.save()
        run.name_tag = 'new_name'
        run.save()
        assert ValidationRun.objects.filter(name_tag='new_name').exists()

    def test_my_results_view(self):
        url = reverse('myruns')
        self.client.login(**self.credentials)
        for i in range(-1, 10):
            response = self.client.get(url, {'page': i})
            self.assertEqual(response.status_code, 200)

        response = self.client.get(url, {'page': 'first'})
        self.assertEqual(response.status_code, 200)

    def test_my_results_view_sorting(self):
        url = reverse('myruns')
        self.client.login(**self.credentials)

        # check some valid sorting keys
        for key in ["start_time",
                    "reference_configuration_id__dataset__pretty_name"]:
            for order in ["asc", "desc"]:
                response = self.client.get(
                    url, {"sort_key": key, "sort_order": order}
                )
                self.assertEqual(response.status_code, 200)

                form = response.context["sorting_form"]
                assert form.cleaned_data["sort_key"] == key
                assert form.cleaned_data["sort_order"] == order

        # check invalid key and missing order
        response = self.client.get(url, {"sort_key": "invalid"})
        self.assertEqual(response.status_code, 200)
        form = response.context["sorting_form"]
        assert form.cleaned_data["sort_key"] == "start_time"
        assert form.cleaned_data["sort_order"] == "desc"

    def test_ajax_get_dataset_options_view(self):
        url = reverse('ajax_get_dataset_options')
        self.client.login(**self.credentials)
        response = self.client.get(url, {'dataset_id': Dataset.objects.get(short_name=globals.GLDAS).id,
                                         'filter_widget_id': 'id_datasets-0-filters',
                                         'param_filter_widget_id': 'id_datasets-0-paramfilters'})
        self.assertEqual(response.status_code, 200)
        return_data = json.loads(response.content)
        assert return_data['versions']
        assert return_data['variables']
        assert return_data['filters']

        response = self.client.get(url, {'dataset_id': ''})
        self.assertEqual(response.status_code, 400)

    def test_ajax_get_version_id_view(self):
        url = reverse('ajax_get_version_id')
        self.client.login(**self.credentials)
        response = self.client.get(url, {'version_id': DatasetVersion.objects.get(short_name=globals.ISMN_V20191211).id})
        self.assertEqual(response.status_code, 200)
        return_data = json.loads(response.content)
        assert return_data['network']

        # another test for dataset other than ISMN
        response = self.client.get(url, {'version_id': DatasetVersion.objects.get(short_name=globals.GLDAS_NOAH025_3H_2_1).id})
        self.assertEqual(response.status_code, 200)
        return_data = json.loads(response.content)
        assert not return_data['network']

        response = self.client.get(url, {'version_id': ''})
        self.assertEqual(response.status_code, 400)

    ## Submit a validation with minimum parameters set
    def test_submit_validation_min(self):
        url = reverse('validation')
        self.client.login(**self.credentials)
        validation_params = {
            'datasets-TOTAL_FORMS': 1,
            'datasets-INITIAL_FORMS': 1,
            'datasets-MIN_NUM_FORMS': 1,
            'datasets-MAX_NUM_FORMS': 5,
            'datasets-0-dataset': Dataset.objects.get(short_name=globals.C3S).id,
            'datasets-0-version': DatasetVersion.objects.get(short_name=globals.C3S_V201706).id,
            'datasets-0-variable': DataVariable.objects.get(short_name=globals.C3S_sm).id,
            'ref-dataset': Dataset.objects.get(short_name=globals.ISMN).id,
            'ref-version': DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id,
            'ref-variable': DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id,
            'scaling_method': ValidationRun.MEAN_STD,
            'scaling_ref': ValidationRun.SCALE_TO_DATA,
        }
        result = self.client.post(url, validation_params)
        self.assertEqual(result.status_code, 302)
        self.assertTrue(result.url.startswith('/result/'))

    ## Submit a validation with all possible parameters set
    def test_submit_validation_max(self):
        test_datasets = [Dataset.objects.get(short_name=globals.C3S),
                         Dataset.objects.get(short_name=globals.ASCAT),
                         Dataset.objects.get(short_name=globals.SMAP),
                         Dataset.objects.get(short_name=globals.C3S),
                         Dataset.objects.get(short_name=globals.ASCAT), ]

        url = reverse('validation')
        self.client.login(**self.credentials)

        # make me one with everything
        validation_params = {
            'datasets-TOTAL_FORMS': len(test_datasets),
            'datasets-INITIAL_FORMS': 1,
            'datasets-MIN_NUM_FORMS': 1,
            'datasets-MAX_NUM_FORMS': 5,

            'ref-dataset': Dataset.objects.get(short_name=globals.ISMN).id,
            'ref-version': DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id,
            'ref-variable': DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id,
            'ref-filter_dataset': True,
            'ref_filters': DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id,
            'ref_filters': DataFilter.objects.get(name='FIL_ISMN_GOOD').id,

            'anomalies': ValidationRun.CLIMATOLOGY,
            'anomalies_from': '1978',
            'anomalies_to': '1998',

            'min_lat': '20.07094414427701',
            'min_lon': '-134.82421875000003',
            'max_lat': '51.47764573196917',
            'max_lon': '-57.83203125000001',

            'interval_from': datetime(1978, 1, 1),
            'interval_to': datetime(1998, 1, 1),

            'scaling_method': ValidationRun.MEAN_STD,
            'scaling_ref': ValidationRun.SCALE_TO_REF,
            'name_tag': 'unit test tag so that I can remember my validation',
        }

        # put in as many datasets as possible
        for ds_no, test_ds in enumerate(test_datasets, start=0):
            ds_dict = {
                'datasets-' + str(ds_no) + '-dataset': test_ds.id,
                'datasets-' + str(ds_no) + '-version': test_ds.versions.first().id,
                'datasets-' + str(ds_no) + '-variable': test_ds.variables.first().id,
                'datasets-' + str(ds_no) + '-filter_dataset': True,
                'datasets-' + str(ds_no) + '-filters': test_ds.filters.last().id,
            }
            validation_params.update(ds_dict)

        result = self.client.post(url, validation_params)
        self.assertEqual(result.status_code, 302)
        self.assertTrue(result.url.startswith('/result/'))

    ## submit a validation with invalid parameters
    def test_submit_validation_invalid(self):
        url = reverse('validation')
        self.client.login(**self.credentials)

        # with only one parameter, we'll get complaints about the missing formset management hidden inputs
        # see https://docs.djangoproject.com/en/2.2/topics/forms/formsets/#understanding-the-managementform
        validation_params = {'scaling_method': 'doesnt exist'}
        result = self.client.post(url, validation_params)
        self.assertEqual(result.status_code, 400)

        ## with a wrong number of dataset configuration forms, we should get an error in the form
        for totalnum in [10, 0]:
            validation_params = {
                'datasets-TOTAL_FORMS': totalnum,
                'datasets-INITIAL_FORMS': 1,
                'datasets-MIN_NUM_FORMS': 1,
                'datasets-MAX_NUM_FORMS': 1000,
                'scaling_method': 'doesnt exist',
            }
            result = self.client.post(url, validation_params)
            self.assertEqual(result.status_code, 200)
            assert result.context['dc_formset']._non_form_errors

    def test_submit_validation_and_cancel(self):
        start_url = reverse('validation')
        self.client.login(**self.credentials)
        validation_params = {
            'datasets-TOTAL_FORMS': 1,
            'datasets-INITIAL_FORMS': 1,
            'datasets-MIN_NUM_FORMS': 1,
            'datasets-MAX_NUM_FORMS': 5,
            'datasets-0-dataset': Dataset.objects.get(short_name=globals.C3S).id,
            'datasets-0-version': DatasetVersion.objects.get(short_name=globals.C3S_V201706).id,
            'datasets-0-variable': DataVariable.objects.get(short_name=globals.C3S_sm).id,
            'ref-dataset': Dataset.objects.get(short_name=globals.GLDAS).id,
            'ref-version': DatasetVersion.objects.get(short_name=globals.GLDAS_NOAH025_3H_2_1).id,
            'ref-variable': DataVariable.objects.get(short_name=globals.GLDAS_SoilMoi0_10cm_inst).id,
            'min_lat': '18.39665',
            'min_lon': '-161.08154',
            'max_lat': '22.91482',
            'max_lon': '-153.91845',
            'scaling_method': ValidationRun.MEAN_STD,
            'scaling_ref': ValidationRun.SCALE_TO_DATA,
        }

        ## start our validation
        result = self.client.post(start_url, validation_params)
        self.assertEqual(result.status_code, 302)

        validation_url = result.url

        match = regex_find('/(result)/(.*)/', result.url)
        assert match
        assert match[0]
        assert match[0][0] == 'result'
        assert match[0][1]

        # let it run a little bit
        time.sleep(1)

        # now let's try out cancelling the validation in it's various forms...
        result_id = match[0][1]
        cancel_url = reverse('stop_validation', kwargs={'result_uuid': result_id})

        # check that the cancel url does something even if we're not DELETEing
        self.client.login(**self.credentials2)
        result = self.client.get(cancel_url)

        # check that nobody but the owner can cancel the validation
        result = self.client.delete(cancel_url)
        self.assertEqual(result.status_code, 403)

        # check that the owner can cancel it
        self.client.login(**self.credentials)
        result = self.client.delete(cancel_url)
        self.assertEqual(result.status_code, 200)

        ## let it settle down
        time.sleep(1)

        # after cancelling, we still get a result for the validation and the cancelled status is indicated
        result = self.client.get(validation_url)
        self.assertEqual(result.status_code, 200)
        cancelled_val = result.context['val']
        self.__logger.info("Progress {}, end time: {}".format(cancelled_val.progress, cancelled_val.end_time))
        assert cancelled_val.progress <= 0

    ## Stress test the server!
    @pytest.mark.long_running
    def no_test_submit_lots_of_validations(self):  # deactivate the test until we found out what makes it hang
        N = 10
        timeout = 300  # seconds
        wait_time = 5  # seconds

        url = reverse('validation')
        self.client.login(**self.credentials)

        validation_params = {
            'data_dataset': Dataset.objects.get(short_name=globals.C3S).id,
            'data_version': DatasetVersion.objects.get(short_name=globals.C3S_V201706).id,
            'data_variable': DataVariable.objects.get(short_name=globals.C3S_sm).id,
            'ref_dataset': Dataset.objects.get(short_name=globals.ISMN).id,
            'ref_version': DatasetVersion.objects.get(short_name=globals.ISMN_V20180712_MINI).id,
            'ref_variable': DataVariable.objects.get(short_name=globals.ISMN_soil_moisture).id,
            # 'scaling_ref': ValidationRun.SCALE_REF,
            'scaling_method': ValidationRun.MEAN_STD,
            'filter_data': True,
            'data_filters': DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id,
            'data_filters': DataFilter.objects.get(name='FIL_C3S_FLAG_0').id,
            'filter_ref': True,
            'ref_filters': DataFilter.objects.get(name='FIL_ALL_VALID_RANGE').id,
            'ref_filters': DataFilter.objects.get(name='FIL_ISMN_GOOD').id,
        }

        result_urls = {}

        self.__logger.info('Starting {} validations from the view...'.format(N))

        ## start lots of validations
        for idx in range(N):
            result = self.client.post(url, validation_params)
            self.assertEqual(result.status_code, 302)

            ## make sure we're redirected to a results page and remember which
            match = regex_find('/(result)/(.*)/', result.url)
            assert match
            assert match[0]
            assert match[0][0] == 'result'
            assert match[0][1]
            result_urls[match[0][1]] = result.url

        ## wait until the validations are finished
        finished_jobs = 0
        runtime = 0
        while finished_jobs < N:
            assert runtime <= timeout, 'Validations are taking too long.'
            self.__logger.info("Validations not finished yet... ({} done)".format(finished_jobs))
            finished_jobs = 0
            # wait a bit and keep track of time
            sleep(wait_time)
            runtime += wait_time
            for uuid, url in result_urls.items():
                validation_run = ValidationRun.objects.get(pk=uuid)
                if validation_run.end_time:
                    finished_jobs += 1

        self.__logger.info("Validations finished now!")

        ## now check the results views for all validations
        for uuid, url in result_urls.items():
            result = self.client.get(url, follow=True)
            self.assertEqual(result.status_code, 200)

            content = result.content.decode('utf-8')

            # make sure there are the expected html elements for a successful validation
            assert content.find('id="result_summary"'), 'No summary'
            assert content.find('id="id_graph_box"'), 'No graphs'
            assert content.find('id="netcdf_box"'), 'No NetCDF download'

            # find the links to the graphs zip and netcdf file
            netcdf_match = regex_find("href='([^']*.nc)'", content)
            zip_match = regex_find("href='([^']*.zip)'", content)
            assert netcdf_match[0], 'No netcdf link found'
            assert zip_match[0], 'No graphs zip link found'

            # check that we can download the graphs zip and netcdf file
            zip_result = self.client.get(zip_match[0], follow=True)
            netcdf_result = self.client.get(netcdf_match[0], follow=True)
            assert zip_result
            assert netcdf_result
            assert zip_result.get('Content-Type') == 'application/zip', 'Wrong mimetype for zip'
            assert netcdf_result.get('Content-Type') == 'application/x-netcdf', 'Wrong mimetype for netcdf'

            # check contents of zipfile
            zip_content = io.BytesIO(b"".join(zip_result.streaming_content))
            zip_file = zipfile.ZipFile(zip_content, 'r')
            self.assertIsNone(zip_file.testzip(), 'Graph zipfile is corrupt')
            assert len(zip_file.namelist()) > 0, 'Nothing in the zipfile'

            # check netcdf file
            netcdf_stream = io.BytesIO(b"".join(netcdf_result.streaming_content))
            assert netcdf_stream, 'netcdf file corrupt'

    def test_access_to_results(self):
        self.client.login(**self.credentials2)

        # try to access other test users result
        url = reverse('result', kwargs={'result_uuid': self.testrun.id})
        response = self.client.get(url)

        # we should be able to see it
        self.assertEqual(response.status_code, 200)

    ## try signing up a new user with all fields given
    def test_signup_new_user_full(self):
        url = reverse('signup')
        user_info = {
            'username': 'chuck_norris',
            'password1': 'Fae6eij7NuoY5Fa1thii',
            'password2': 'Fae6eij7NuoY5Fa1thii',
            'email': 'chuck@norris.com',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'organisation': 'Texas Rangers',
            'country': 'US',
            'orcid': '0000-0002-1825-0097',
            'terms_consent': True,
        }
        result = self.client.post(url, user_info)
        self.assertEqual(result.status_code, 302)
        self.assertRedirects(result, reverse('signup_complete'))

    ## try signing up a new user and giving only the required fields
    def test_signup_new_user_minimal(self):
        url = reverse('signup')
        user_info = {
            'username': 'chuck_norris',
            'password1': 'Fae6eij7NuoY5Fa1thii',
            'password2': 'Fae6eij7NuoY5Fa1thii',
            'email': 'chuck@norris.com',
            'terms_consent': True,
        }
        result = self.client.post(url, user_info)
        self.assertEqual(result.status_code, 302)
        self.assertRedirects(result, reverse('signup_complete'))

    ## make sure the user has to check the terms consent box
    def test_signup_new_user_no_consent(self):
        url = reverse('signup')
        user_info = {
            'username': 'chuck_norris',
            'password1': 'Fae6eij7NuoY5Fa1thii',
            'password2': 'Fae6eij7NuoY5Fa1thii',
            'email': 'chuck@norris.com',
            'terms_consent': False,
        }
        result = self.client.post(url, user_info)
        self.assertEqual(result.status_code, 200)

    def test_update_user_profile(self):
        self.client.login(**self.credentials)

        url = reverse('user_profile')
        user_info = {
            'username': self.credentials['username'],
            'email': 'chuck@norris.com',
            'country': 'AT',
            'orcid': '0000-0002-1825-0097',
            'last_name': 'Chuck',
            'first_name': 'Norris',
            'organisation': 'Texas Rangers',
        }
        result = self.client.post(url, user_info)
        self.assertEqual(result.status_code, 302)
        self.assertRedirects(result, reverse('user_profile_updated'))

    def test_update_user_profile_fail(self):
        self.client.login(**self.credentials)

        url = reverse('user_profile')
        user_info = {
            'username': self.credentials['username'],  ## this is too little info, should fail
        }
        result = self.client.post(url, user_info)
        self.assertEqual(result.status_code, 200)

    def test_user_profile_form_validation(self):
        form_data = {'username': 'john_doe',
                     'password1': 'asd12N83poLL',
                     'password2': 'asd12N83poLL',
                     'country': 'AT',
                     'last_name': 'Doe',
                     'first_name': 'John',
                     'organisation': '????',
                     'email': 'john@nowhere.com',
                     'orcid': '0000-0002-1825-0097',
                     }
        form = UserProfileForm(initial={'username': 'john_doe', }, data=form_data)
        self.assertTrue(form.is_valid())  # should pass

        form_data = {'email': 'john@nowhere.com'}
        form = UserProfileForm(initial={'username': 'john_doe', }, data=form_data)
        self.assertTrue(form.is_valid())  # should pass

        form_data = {'username': 'john_doe'}
        form = UserProfileForm(initial={'username': 'john_doe', }, data=form_data)
        self.assertFalse(form.is_valid())  # should fail because of the missing e-mail field

        form_data = {'username': 'john_doe',
                     'password1': 'asd12N83poLL',
                     'password2': 'asd12N83poLL',
                     'email': 'john@nowhere.com'
                     }
        form = UserProfileForm(initial={'username': 'john_doe', }, data=form_data)
        self.assertTrue(form.is_valid())  # should pass

        form_data = {'username': 'john_doe',
                     'password1': 'asd12N83poLL',
                     'password2': 'asd12N8',
                     'email': 'john@nowhere.com'
                     }
        form = UserProfileForm(initial={'username': 'john_doe', }, data=form_data)
        self.assertFalse(form.is_valid())  # should fail because passwords don't match

    def test_deactivate_user_profile(self):
        url = reverse('user_profile')
        credentials = {
            'username': 'to_be_deactivated',
            'password': 'secret'}
        to_be_deactivated = User.objects.create_user(**credentials)
        to_be_deactivated.is_active = True
        to_be_deactivated.save()
        self.client.login(**credentials)
        result = self.client.delete(url)
        to_be_deactivated.refresh_from_db()
        self.assertEqual(to_be_deactivated.is_active, False)
        self.assertEqual(result.status_code, 200)
        login_success = self.client.login(**credentials)
        assert not login_success

    ## simulate workflow for password reset
    def test_password_reset(self):
        ## pattern to get the password reset link from the email
        reset_url_pattern = reverse('password_reset_confirm', kwargs={'uidb64': 'DUMMY', 'token': 'DUMMY'})
        reset_url_pattern = reset_url_pattern.replace('DUMMY', '([^/]+)')

        orig_password = self.credentials2['password']

        ## go to the password reset page
        url = reverse('password_reset')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        ## send it the user's email
        response = self.client.post(url, {'email': self.credentials2['email'], })
        self.assertRedirects(response, reverse('password_reset_done'))

        ## make sure the right email got sent with correct details
        sent_mail = mail.outbox[0]  # @UndefinedVariable
        assert sent_mail
        assert sent_mail.subject
        assert sent_mail.body
        assert sent_mail.from_email == settings.EMAIL_FROM
        assert self.credentials2['email'] in sent_mail.to
        assert self.credentials2['username'] in sent_mail.body

        ## check that the email contains a confirmation link with userid and token
        urls = regex_find(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          sent_mail.body)
        userid = None
        token = None
        for u in urls:
            rmatch = regex_find(reset_url_pattern, u)
            if rmatch:
                userid = rmatch[0][0]
                token = rmatch[0][1]

        assert userid
        assert token

        ## now try to use the link in the email several times - should only be successful the first time
        for i in range(1, 3):
            ## go to the confirmation link given in the email
            url = reverse('password_reset_confirm', kwargs={'uidb64': userid, 'token': token})
            response = self.client.get(url)

            ## first time
            if i == 1:
                self.assertEqual(response.status_code, 302)
                ## follow redirect and enter new password - we should be redirected to password_reset_complete
                url = response.url
                self.credentials2['password'] = '1superPassword!!'
                response = self.client.post(url, {'new_password1': self.credentials2['password'],
                                                  'new_password2': self.credentials2['password'], })
                self.assertRedirects(response, reverse('password_reset_complete'))
            ## second time
            else:
                ## no redirect and message that reset wasn't successful
                self.assertEqual(response.status_code, 200)
                assert response.context['title'] == 'Password reset unsuccessful'

        ## make sure we can log in with the new password
        login_success = self.client.login(**self.credentials2)
        assert login_success

        ## make sure we can't log in with the old password
        login_success = self.client.login(**{'username': self.credentials2['username'], 'password': orig_password})
        assert not login_success
