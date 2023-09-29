from django.conf.urls import re_path
from django.urls import path, include

from api.views.data_filter_view import data_filter, data_parameterised_filter, data_filter_by_datasetversion
# data_parameterised_filter_by_config
# from api.views.data_filter_view data_filter_by_id, data_parameterised_filter_by_id
from api.views.dataset_variable_view import dataset_variable, dataset_variable_by_id, dataset_variable_by_dataset
from api.views.dataset_version_geojson import dataset_version_geojson_by_id
from api.views.dataset_version_view import dataset_version, dataset_version_by_id, dataset_version_by_dataset
from api.views.dataset_view import dataset, dataset_by_id
from api.views.ismn_network_view import get_ismn_networks
from api.views.login_view import api_login
from api.views.logout_view import api_logout
from api.views.path_var_test_endpoint import path_var_get
from api.views.validation_config_view import start_validation, get_validation_configuration, get_scaling_methods
from api.views.uptime_view import uptime_ping, get_uptime
from api.views.comparison_view import get_comparison_table, get_comparison_plots_for_metric, \
    download_comparison_table, get_comparison_metrics, get_spatial_extent
from api.views.user_view import signup_post, user_update, user_delete
from api.views.validation_run_view import published_results, my_results, validation_run_by_id, \
    custom_tracked_validation_runs, get_validations_for_comparison, get_copied_validations
from api.views.dataset_configuration_view import dataset_configuration, dataset_configuration_by_validation
from api.views.global_params_view import global_params
from api.views.modify_validation_view import *
from api.views.serving_file_view import *
from api.views.local_api_view import get_list_of_countries
from api.views.settings_view import backend_settings
from api.views.upload_user_data_view import *
from api.views.support_request_view import *
from api.views.custom_dataset_view import *

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Snippets API",
#         default_version='v1',
#         description="Test description",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="contact@snippets.local"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [

    # url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # IMPORTANT
    # URLs should not end with a slash. If you add a new endpoint, do not add a trailing slash:
    #   GOOD:  path('my-new-endpoint', my_new_view, name='fancy stuff'),
    #   WRONG: path('my-new-endpoint/', my_new_view, name='fancy stuff'),
    #
    re_path(r'^path_test/(?P<username>.+)$', path_var_get),
    path('auth/login', api_login, name='api-login'),
    path('auth/logout', api_logout, name='api-logout'),
    path('dataset', dataset, name='Datasets'),
    re_path(r'^dataset/(?P<id>.+)$', dataset_by_id),
    path('dataset-version', dataset_version, name='Dataset version'),
    re_path(r'^dataset-version/(?P<version_id>.+)$', dataset_version_by_id),
    re_path(r'^dataset-version-by-dataset/(?P<dataset_id>.+)$', dataset_version_by_dataset,
            name='Dataset version by dataset'),
    path('dataset-variable', dataset_variable, name='Dataset variable'),
    re_path(r'^dataset-variable/(?P<variable_id>.+)$', dataset_variable_by_id),
    re_path(r'^dataset-variable-by-dataset/(?P<dataset_id>.+)$', dataset_variable_by_dataset,
            name='Dataset_variable_by_dataset'),
    path('published-results', published_results, name='Published results'),
    re_path(r'^validation-runs/(?P<id>.+)$', validation_run_by_id, name='Validation run by id'),
    path('dataset-configuration', dataset_configuration, name='Configuration'),
    re_path(r'^dataset-configuration/(?P<validation_id>.+)$', dataset_configuration_by_validation,
            name='Configuration'),
    path('data-filter', data_filter, name='Dataset filters'),
    re_path(r'^data-filter/(?P<version_id>.+)$', data_filter_by_datasetversion),
    path('globals', global_params, name='Global context'),
    path('my-results', my_results, name='My results'),
    re_path(r'^validation-configuration/(?P<id>.+)$', get_validation_configuration, name='Validation configuration'),
    path('validation-configuration', start_validation, name='Run new validation'),
    path('param-filter', data_parameterised_filter, name='Parameterised filter'),
    path('stop-validation/<uuid:result_uuid>', stop_validation, name='Stop validation'),
    path('custom-tracked-run', custom_tracked_validation_runs, name='Copied custom run'),
    path('table-comparison', get_comparison_table, name='Comparison table'),
    path('plots-comparison', get_comparison_plots_for_metric, name='Comparison plots'),
    path('image-comparison', get_spatial_extent, name='Extent image'),
    path('metrics-for-comparison', get_comparison_metrics, name='Comparison metrics'),
    path('download-comparison-table', download_comparison_table, name='Download comparison csv'),
    path('delete-validation/<uuid:result_uuid>/', delete_result, name='Delete validation'),
    path('change-validation-name/<uuid:result_uuid>/', change_name, name='Change name'),
    path('archive-result/<uuid:result_uuid>/', archive_result, name='Archive results'),
    path('extend-result/<uuid:result_uuid>/', extend_result, name='Extend results'),
    path('publish-result/<uuid:result_uuid>/', publish_result, name='Publish result'),
    path('add-validation/<uuid:result_uuid>/', add_validation, name='Add validation'),
    path('remove-validation/<uuid:result_uuid>/', remove_validation, name='Remove validation'),
    path('custom-tracked-run', custom_tracked_validation_runs, name='Tracked custom run'),
    path('download-result', get_results, name='Download results'),
    path('summary-statistics', get_summary_statistics, name='Summary statistics'),
    path('download-statistics-csv', get_csv_with_statistics, name='Download statistics csv'),
    path('uptime-ping', uptime_ping),
    path('uptime-report', get_uptime),
    path('get-graphic-files', get_graphic_files, name='Get graphic files'),
    path('get-metric-and-plots-names', get_metric_names_and_associated_files, name='Get metric and plots names'),
    path('validation-runs-for-comparison', get_validations_for_comparison, name='Get validations for comparison'),
    path('country-list', get_list_of_countries, name='List of countries'),
    path('sign-up', signup_post, name='Sign up'),
    path('user-update', user_update, name='User update'),
    path('user-delete', user_delete, name='User delete'),
    path('settings', backend_settings, name="Settings"),
    path('get-graphic-file', get_graphic_file, name='Get graphic file'),
    path('publishing-form', get_publishing_form, name='Get publishing form'),
    path('copy-validation', copy_validation_results, name='Copy validation results'),
    re_path(r'^copied-validation-record/(?P<id>.+)$', get_copied_validations, name='Copied run record'),
    path('password-reset', include('django_rest_passwordreset.urls', namespace='password-reset')),
    path('ismn-network', get_ismn_networks, name='Get ISMN networks'),
    path('upload-user-data/<str:filename>/', upload_user_data, name='Upload user data'),
    path('get-list-of-user-data-files', get_list_of_user_data_files, name='Get User Data Files'),
    path('delete-entire-dataset/<str:file_uuid>/', delete_user_dataset_and_file, name='Delete User Data File'),
    path('get-user-file-by-id/<uuid:file_uuid>/', get_user_data_file_by_id,
         name='Get user file by ID'),
    path('update-metadata/<uuid:file_uuid>/', update_metadata, name='Update metadata'),
    path('scaling-methods', get_scaling_methods, name='Scaling methods'),
    path('support-request', send_support_request, name='Support request'),
    re_path(r'^dataset-version-geojson/(?P<version_id>.+)$', dataset_version_geojson_by_id),
    path('support-request', send_support_request, name='Support request'),
    path('data-management-groups', get_data_management_groups, name='Get data management groups'),
    path('manage-data-in-management-group', manage_data_in_group,
         name='Add data to management groups'),
    path('delete-only-datafile/<str:file_uuid>/', delete_dataset_file_only, name='Delete User Data File Only'),
    path('delete-multiple-validations', delete_multiple_result, name='Delete Multiple Validations'),
    # path('test-user-dataset/<str:dataset_id>/', test_user_data, name='Test user data'),
    # path('validate-user-data', validate_user_data, name='Validate user data'),
]
