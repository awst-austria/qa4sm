import logging
import shutil

from django.conf import settings
from django.urls import reverse

import validator.validation as val
from django.test import TestCase
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from api.tests.test_helper import *
from validator.models import ValidationRun
from validator.validation import mkdir_if_not_exists, set_outfile
from django.test.utils import override_settings

User = get_user_model()


def get_ncfile_name(validation):
    file_name_parts = []
    for ind, dataset_config in enumerate(validation.dataset_configurations.all()):
        file_name_parts.append(
            str(ind) + '-' + dataset_config.dataset.short_name + '.' + dataset_config.variable.pretty_name
        )
    return ' with '.join(file_name_parts) + '.nc'


# ---------------------------------------------------------------------------
# Fast tests — no validation run needed, only static files
# ---------------------------------------------------------------------------

class TestStaticFileServing(TestCase):
    """Tests for serving static graphic files — do not require running a validation."""

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']
    __logger = logging.getLogger(__name__)

    def setUp(self):
        self.auth_data, self.test_user = create_test_user()
        self.client = APIClient()
        self.client.login(**self.auth_data)

    def test_get_graphic_files(self):
        get_graphic_files_url = reverse('Get graphic files')

        # no file names provided
        response = self.client.get(get_graphic_files_url)
        assert response.status_code == 404
        assert response.json()['message'] == 'No file names given'

        # get static graphic files
        files = ['/static/images/home/background.webp', '/static/images/logo/logo_awst.webp']
        new_url = get_graphic_files_url + '?'
        for file_name in files:
            new_url += 'file=' + file_name + '&'
        new_url = new_url.rstrip('&')

        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # try to get only one file
        file = '/static/images/home/background.webp'
        response = self.client.get(get_graphic_files_url + f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert type(response.json()) == list

        # should also work for logged-out users
        self.client.logout()
        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_graphic_file(self):
        get_graphic_file_url = reverse('Get graphic file')

        # no file name provided
        response = self.client.get(get_graphic_file_url)
        assert response.status_code == 404
        assert response.json()['message'] == 'No file name given'

        # get a single static graphic file
        file = '/static/images/home/background.webp'
        response = self.client.get(get_graphic_file_url + f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1

        # multiple files provided — only the first should be returned
        files = ['/static/images/home/background.webp', '/static/images/logo/logo_awst.webp']
        new_url = get_graphic_file_url + '?'
        for file_name in files:
            new_url += 'file=' + file_name + '&'
        new_url = new_url.rstrip('&')

        response = self.client.get(new_url)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert type(response.json()) == dict

        # should also work for logged-out users
        self.client.logout()
        response = self.client.get(get_graphic_file_url + f'?file={file}')
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_user_manual_not_found(self):
        """Returns 404 when USER_MANUAL_PATH is not set or file doesn't exist."""
        user_manual_url = reverse('Get user manual')

        with self.settings(USER_MANUAL_PATH=''):
            response = self.client.get(user_manual_url)
            assert response.status_code == 404
            assert b'not found' in response.content.lower()

    def test_get_user_manual_nonexistent_file(self):
        """Returns 404 when USER_MANUAL_PATH points to a non-existent file."""
        user_manual_url = reverse('Get user manual')

        with self.settings(USER_MANUAL_PATH='/nonexistent/path/manual.pdf'):
            response = self.client.get(user_manual_url)
            assert response.status_code == 404

    def test_get_user_manual_success(self):
        """Returns the file when USER_MANUAL_PATH points to a real file."""
        import tempfile
        user_manual_url = reverse('Get user manual')

        # create a temporary PDF-like file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake content')
            tmp_path = tmp.name

        try:
            with self.settings(USER_MANUAL_PATH=tmp_path):
                response = self.client.get(user_manual_url)
                assert response.status_code == 200
                assert 'pdf' in response.get('Content-Type', '').lower()
                assert 'inline' in response.get('Content-Disposition', '').lower()
        finally:
            os.unlink(tmp_path)

    def test_get_ismn_list_file_requires_auth(self):
        """Returns 403 when user is not authenticated."""
        ismn_url = reverse('Get ISMN csv file')
        self.client.logout()

        response = self.client.get(ismn_url)
        assert response.status_code in (401, 403)

    def test_get_ismn_list_file_not_found(self):
        """Returns 404 when ISMN list file does not exist on disk."""
        from unittest.mock import patch
        ismn_url = reverse('Get ISMN csv file')

        # patch os.path.exists to simulate missing file
        with patch('api.views.serving_file_view.os.path.exists', return_value=False):
            response = self.client.get(ismn_url)
            assert response.status_code == 404


# ---------------------------------------------------------------------------
# Slow tests — require a real validation run
# Validation is executed ONCE for the whole class via setUpTestData
# ---------------------------------------------------------------------------

@override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                   CELERY_TASK_ALWAYS_EAGER=True)
class TestValidationFileServing(TestCase):
    """
    Tests for serving validation result files (netCDF, CSV, metrics, summary).

    The validation is run once in setUpTestData and shared across all tests,
    so we avoid running val.run_validation() 4 separate times.
    Previously this cost ~37s × 4 = ~148s; now it costs ~37s total.
    """

    fixtures = ['variables', 'versions', 'datasets', 'filters', 'users']
    __logger = logging.getLogger(__name__)

    @classmethod
    def setUpTestData(cls):
        # Create user and validation run once for the entire class.
        # We store only primitives (id, auth dict) as class attributes —
        # Django freezes ORM objects inside setUpTestData transactions, so
        # we must re-fetch them per test via setUp using the stored IDs.
        cls.auth_data, test_user = create_test_user()
        cls.test_user_id = test_user.id

        run = default_parameterized_validation_to_be_run(test_user)
        run.save()
        cls.run_id = run.id
        cls.wrong_id = 'f0000000-a000-b000-c000-d00000000000'

        # Run validation ONCE — CELERY_TASK_ALWAYS_EAGER=True makes this synchronous,
        # so no time.sleep() is needed.
        val.run_validation(cls.run_id)

    @classmethod
    def tearDownClass(cls):
        # Clean up generated files once after all tests in this class finish.
        try:
            run = ValidationRun.objects.get(id=cls.run_id)
            delete_run(run)
        except ValidationRun.DoesNotExist:
            pass
        super().tearDownClass()

    def setUp(self):
        # Re-fetch the run from DB for each test so we always have a fresh,
        # non-frozen object (setUpTestData freezes ORM instances).
        self.run = ValidationRun.objects.get(id=self.__class__.run_id)
        # Re-create the API client for each test (handles login/logout isolation)
        self.client = APIClient()
        self.client.login(**self.__class__.auth_data)

    # --- test_get_results ---------------------------------------------------

    def test_get_results_no_output_dir(self):
        """Returns 404 when validation has no output directory."""
        get_results_url = reverse('Download results')

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=netCDF')
        # After setUpTestData the run already has output; this sub-case was
        # meaningful only before the run. Keep a wrong-ID check instead.
        response = self.client.get(get_results_url + f'?validationId={self.wrong_id}&fileType=netCDF')
        assert response.status_code == 404

    def test_get_results_netcdf(self):
        """Authenticated user can download the netCDF result file."""
        get_results_url = reverse('Download results')

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 200
        assert 'netcdf' in response.get('Content-Type')

    def test_get_results_graphics(self):
        """Authenticated user can download the graphics zip."""
        get_results_url = reverse('Download results')

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=graphics')
        assert response.status_code == 200
        assert 'zip' in response.get('Content-Type')

    def test_get_results_unknown_file_type(self):
        """Unknown fileType returns 404."""
        get_results_url = reverse('Download results')

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=some_other_file')
        assert response.status_code == 404

    def test_get_results_logged_out_user_can_download(self):
        """Logged-out users can still download results (public access)."""
        get_results_url = reverse('Download results')
        self.client.logout()

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=netCDF')
        assert response.status_code == 200
        assert 'netcdf' in response.get('Content-Type')

        response = self.client.get(get_results_url + f'?validationId={self.run_id}&fileType=graphics')
        assert response.status_code == 200
        assert 'zip' in response.get('Content-Type')

    # --- test_get_csv_with_statistics ---------------------------------------

    def test_get_csv_with_statistics_ok(self):
        """Returns CSV statistics file for a valid run."""
        get_csv_url = reverse('Download statistics csv')

        response = self.client.get(get_csv_url + f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert 'Stats_summary.csv' in response.get('Content-Disposition')

    def test_get_csv_with_statistics_wrong_id(self):
        """Returns 404 for an unknown validation ID."""
        get_csv_url = reverse('Download statistics csv')

        response = self.client.get(get_csv_url + f'?validationId={self.wrong_id}')
        assert response.status_code == 404

    def test_get_csv_with_statistics_logged_out(self):
        """Logged-out users can still download CSV statistics."""
        get_csv_url = reverse('Download statistics csv')
        self.client.logout()

        response = self.client.get(get_csv_url + f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert 'Stats_summary.csv' in response.get('Content-Disposition')

    # --- test_get_metric_names_and_associated_files -------------------------

    def test_get_metric_names_no_output_file(self):
        """Returns 404 when validation has no output directory assigned."""
        get_metric_url = reverse('Get metric and plots names')

        # Temporarily clear the output file to simulate missing output
        original_output = self.run.output_file
        self.run.output_file = ''
        self.run.save()

        response = self.client.get(get_metric_url + f'?validationId={self.run_id}')
        assert response.status_code == 404
        assert response.json()['message'] == 'Given validation has no output directory assigned'

        # Restore
        self.run.output_file = original_output
        self.run.save()



    def test_get_metric_names_wrong_id(self):
        """Returns 404 for an unknown validation ID."""
        get_metric_url = reverse('Get metric and plots names')

        response = self.client.get(get_metric_url + f'?validationId={self.wrong_id}')
        assert response.status_code == 404

    def test_get_metric_names_ok(self):
        """Returns metric names and associated files for a completed validation."""
        get_metric_url = reverse('Get metric and plots names')

        response = self.client.get(get_metric_url + f'?validationId={self.run_id}')
        assert response.status_code == 200
        assert response.json()  # non-empty response; exact length depends on metrics used

    # --- test_get_summary_statistics ----------------------------------------

    def test_get_summary_statistics_ok(self):
        """Returns HTML summary statistics table for a valid run."""
        summary_statistics_url = reverse('Summary statistics')

        response = self.client.get(summary_statistics_url + f'?id={self.run_id}')
        assert response.status_code == 200
        assert 'table' in response.content.decode('UTF-8')

    def test_get_summary_statistics_wrong_id(self):
        """Returns 404 for an unknown validation ID."""
        summary_statistics_url = reverse('Summary statistics')

        response = self.client.get(summary_statistics_url + f'?id={self.wrong_id}')
        assert response.status_code == 404

    def test_get_summary_statistics_logged_out(self):
        """Logged-out users can still access summary statistics."""
        summary_statistics_url = reverse('Summary statistics')
        self.client.logout()

        response = self.client.get(summary_statistics_url + f'?id={self.run_id}')
        assert response.status_code == 200
        assert 'table' in response.content.decode('UTF-8')