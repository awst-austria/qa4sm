from django.conf.urls import url
from django.urls import path

from api.views.data_filter_view import data_filter, data_parameterised_filter, data_filter_by_dataset
    # data_parameterised_filter_by_config
# from api.views.data_filter_view data_filter_by_id, data_parameterised_filter_by_id
from api.views.dataset_variable_view import dataset_variable, dataset_variable_by_id, dataset_variable_by_dataset
from api.views.dataset_version_view import dataset_version, dataset_version_by_id, dataset_version_by_dataset
from api.views.dataset_view import dataset, dataset_by_id
from api.views.login_view import api_login
from api.views.logout_view import api_logout
from api.views.path_var_test_endpoint import path_var_get
from api.views.validation_config_view import start_validation, get_validation_configuration
from api.views.uptime_view import uptime_ping, get_uptime
from api.views.user_view import users, signup_post, user_modify
from api.views.validation_run_view import published_results, my_results, validation_run_by_id, validation_runs, \
    custom_tracked_validation_runs, get_summary_statistics, get_publishing_form, copy_validation_results
from api.views.dataset_configuration_view import dataset_configuration, dataset_configuration_by_dataset
from api.views.global_params_view import global_params
from api.views.modify_validation_view import stop_validation, modify_result, change_name, archive_result, \
    extend_result, publish_result, add_validation, remove_validation
from api.views.serving_file_view import get_results, get_csv_with_statistics, get_graphic_files, \
    get_metric_names_and_associated_files, get_graphic_file
from api.views.local_api_view import get_list_of_countries
from api.views.settings_view import settings


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
    url(r'^test$', users),
    url(r'^path_test/(?P<username>.+)$', path_var_get),
    path('user', users, name='Users'),
    path('auth/login', api_login, name='api-login'), # checked
    path('auth/logout', api_logout, name='api-logout'),
    path('dataset', dataset, name='Datasets'),
    url(r'^dataset/(?P<id>.+)$', dataset_by_id),
    path('dataset-version', dataset_version, name='Dataset version'), # checked
    url(r'^dataset-version/(?P<version_id>.+)$', dataset_version_by_id), # checked
    url(r'^dataset-version-by-dataset/(?P<dataset_id>.+)$', dataset_version_by_dataset, name='Dataset version by dataset'), # checked
    path('dataset-variable', dataset_variable, name='Dataset variable'), # checked
    url(r'^dataset-variable/(?P<variable_id>.+)$', dataset_variable_by_id), # checked
    url(r'^dataset-variable-by-dataset/(?P<dataset_id>.+)$', dataset_variable_by_dataset, name='Dataset_variable_by_dataset'),
    path('published-results', published_results, name='Published results'),
    path('validation-runs', validation_runs, name='All validation runs (results)'),
    url(r'^validation-runs/(?P<id>.+)$', validation_run_by_id),
    path('dataset-configuration', dataset_configuration, name='Configuration'), # checked
    url(r'^dataset-configuration/(?P<dataset_id>.+)$', dataset_configuration_by_dataset, name='Configuration'), # checked
    path('data-filter', data_filter, name='Dataset filters'),  # checked
    url(r'^data-filter/(?P<dataset_id>.+)$', data_filter_by_dataset), # checked
    path('globals', global_params, name='Global context'), # checked
    path('my-results', my_results, name='My results'),
    url(r'^validation-configuration/(?P<id>.+)$', get_validation_configuration),
    path('validation-configuration', start_validation, name='Run new validation'),
    path('param-filter', data_parameterised_filter, name='Parameterised filter'),  # checked
    path('stop-validation/<uuid:result_uuid>', stop_validation, name='Stop validation'),  # checked
    path('modify-validation/<uuid:result_uuid>/', modify_result, name='Modify result'),  # checked
    path('change-validation-name/<uuid:result_uuid>/', change_name, name='Change name'), # checked
    path('archive-result/<uuid:result_uuid>/', archive_result, name='Archive results'), # checked
    path('extend-result/<uuid:result_uuid>/', extend_result, name='Extend results'), # checked
    path('publish-result/<uuid:result_uuid>/', publish_result, name='Publish results'), # checked
    path('add-validation/<uuid:result_uuid>/', add_validation, name='Add validation'), # checked
    path('remove-validation/<uuid:result_uuid>/', remove_validation, name='Add validation'), # checked
    path('custom-tracked-run', custom_tracked_validation_runs, name='Copied custom run'),
    path('download-result', get_results, name='Download results'),
    path('summary-statistics', get_summary_statistics, name='Summary statistics'),
    path('download-statistics-csv', get_csv_with_statistics, name='Download statistics csv'),
    path('uptime-ping', uptime_ping),
    path('uptime-report', get_uptime),
    path('get-graphic-files', get_graphic_files, name='Get graphic file'),
    path('get-metric-and-plots-names', get_metric_names_and_associated_files, name='Get metric and plots names'),
    path('country-list', get_list_of_countries, name = 'List of countries'), #checked
    path('sign-up', signup_post, name='Sign up'),
    path('user-modify', user_modify, name='User update'),
    path('settings', settings, name="Settings"),
    path('get-graphic-file', get_graphic_file, name='Get graphic file'),
    path('publishing-form', get_publishing_form, name='Get publishing form'),
    path('copy-validation', copy_validation_results, name='Copy validation results'),
]
