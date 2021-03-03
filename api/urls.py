from django.conf.urls import url
from django.urls import path

from api.views.data_filter_view import data_filter
from api.views.dataset_variable_view import dataset_variable
from api.views.dataset_version_view import dataset_version
from api.views.dataset_view import dataset
from api.views.login_view import api_login
from api.views.logout_view import api_logout
from api.views.path_var_test_endpoint import path_var_get
from api.views.start_validation_view import start_validation
from api.views.user_view import users
from api.views.validation_run_view import published_results, my_results
from api.views.dataset_configuration_view import dataset_configuration
from api.views.global_params_view import global_params

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
    path('auth/login', api_login, name='login'),
    path('auth/logout', api_logout, name='logout'),
    path('dataset', dataset, name='Datasets'),
    path('dataset-version', dataset_version, name='Dataset versions'),
    path('dataset-variable', dataset_variable, name='Dataset variables'),
    path('published-results', published_results, name='Published results'),
    path('dataset-configuration', dataset_configuration, name='Configuration'),
    path('data-filter', data_filter, name='Dataset filters'),
    path('globals', global_params, name='Global context'),
    path('my-results', my_results, name='My results'),
    path('run-validation', start_validation, name='Run new validation')

]
