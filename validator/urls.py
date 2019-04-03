from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup_complete/', views.signup_complete, name='signup_complete'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html', email_template_name='auth/password_reset_email.html', subject_template_name='auth/password_reset_subject.txt', extra_email_context={'password_reset_timeout_days': settings.PASSWORD_RESET_TIMEOUT_DAYS}), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),

    path('alpha/', views.alpha, name='alpha'),
    path('terms/', views.terms, name='terms'),
    path('datasets/', views.datasets, name='datasets'),
    path('help/', views.userhelp, name='help'),
    path('about/', views.about, name='about'),

    path('', views.home, name='home'),
    path('myruns/', views.user_runs, name='myruns'),
    path('validate/', views.validation, name='validation'),
    path('validate/<uuid:result_uuid>', views.stop_validation, name='stop_validation'),
    path('result/<uuid:result_uuid>/', views.result, name='result'),

    path('ajax/get-dataset-options/', views.ajax_get_dataset_options, name='ajax_get_dataset_options'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
