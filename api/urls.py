from django.conf.urls import url
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.endpoints.LoginView import api_login
from api.endpoints.PathVarTestEndpoint import path_var_get
from api.endpoints.UsersView import users_get

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path('swagger-ui/', TemplateView.as_view(template_name='swagger.html',
    #                                          extra_context={'schema_url': 'openapi-schema'}), name='swagger-ui'),
    # path('openapi', get_schema_view(
    #     title="Your Project",
    #     description="API for all things …",
    #     version="1.0.0"
    # ), name='openapi-schema'),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    url(r'^test/$', users_get),
    url(r'^path_test/(?P<username>.+)/$', path_var_get),
    path('auth', api_login, name='login'),


    # path('auth/', LoginView.as_view(), name='login'),
]
