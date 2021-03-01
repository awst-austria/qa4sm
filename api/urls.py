from django.conf.urls import url
from django.urls import path

from api.views.DataFilterView import data_filter
from api.views.DatasetVariableView import dataset_variable
from api.views.DatasetVersionView import dataset_version
from api.views.DatasetView import dataset
from api.views.LoginView import api_login
from api.views.LogoutView import api_logout
from api.views.PathVarTestEndpoint import path_var_get
from api.views.UserView import users
from api.views.ValidationRunView import published_results, my_results
from api.views.DatasetConfigurationView import dataset_configuration
from api.views.GlobalParamsView import global_params

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
    path('my-results', my_results, name= 'My results')

]
