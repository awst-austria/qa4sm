from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='validator/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('signup/', views.signup, name='signup'),
    path('signup_complete/', views.signup_complete, name='signup_complete'),
    path('alpha/', views.alpha, name='alpha'),
    path('terms/', views.terms, name='terms'),
    path('datasets/', views.datasets, name='datasets'),

    path('', views.home, name='home'),
    path('myruns/', views.user_runs, name='myruns'),
    path('validate/', views.validation, name='validation'),
    path('result/<uuid:result_uuid>/', views.result, name='result'),
    path('help/', views.userhelp, name='help'),
    path('about/', views.about, name='about'),

    path('ajax/get-dataset-options/', views.ajax_get_dataset_options, name='ajax_get_dataset_options'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
