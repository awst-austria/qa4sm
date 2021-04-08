from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from api.views.data_filter_view import data_filter, data_filter_by_id, data_parameterised_filter_by_id, \
    data_parameterised_filter
from api.views.dataset_variable_view import dataset_variable, dataset_variable_by_id
from api.views.dataset_version_view import dataset_version, dataset_version_by_id
from api.views.dataset_view import dataset, dataset_by_id
from api.views.login_view import api_login
from api.views.logout_view import api_logout
from api.views.path_var_test_endpoint import path_var_get
from api.views.start_validation_view import start_validation
from api.views.user_view import users
from api.views.validation_run_view import published_results, my_results, validation_run_by_id, validation_runs,\
    custom_tracked_validation_runs
from api.views.dataset_configuration_view import dataset_configuration
from api.views.global_params_view import global_params
from api.views.modify_validation_view import stop_validation, modify_result

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
    path('auth/login', api_login, name='api-login'),
    path('auth/logout', api_logout, name='api-logout'),
    path('dataset', dataset, name='Datasets'),
    url(r'^dataset/(?P<id>.+)$', dataset_by_id),
    path('dataset-version', dataset_version, name='Dataset versions'),
    url(r'^dataset-version/(?P<id>.+)$', dataset_version_by_id),
    path('dataset-variable', dataset_variable, name='Dataset variables'),
    url(r'^dataset-variable/(?P<id>.+)$', dataset_variable_by_id),
    path('published-results', published_results, name='Published results'),
    path('validation-runs', validation_runs, name='All validation runs (results)'),
    url(r'^validation-runs/(?P<id>.+)$', validation_run_by_id),
    path('dataset-configuration', dataset_configuration, name='Configuration'),
    path('data-filter', data_filter, name='Dataset filters'),
    path('globals', global_params, name='Global context'),
    path('my-results', my_results, name='My results'),
    path('run-validation', start_validation, name='Run new validation'),
    url(r'^data-filter/(?P<id>.+)$', data_filter_by_id),
    path('param-filter', data_parameterised_filter, name='Parameterised filter'),
    url(r'^param-filter/(?P<id>.+)$', data_parameterised_filter_by_id),
    path('stop-validation/<uuid:result_uuid>', stop_validation, name='Stop validation'),
    path('modify-validation/<uuid:result_uuid>/', modify_result, name='Result'),
    path('custom-copied-run', custom_tracked_validation_runs, name='Copied run')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
