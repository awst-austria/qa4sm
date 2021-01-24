from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from api.endpoints.test import TestEndpoint

urlpatterns = [
    path('test/', TestEndpoint.as_view()),
]
