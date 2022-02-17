"""valentina URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic.base import RedirectView
from django.urls import include, path

from django.conf import settings

from api.frontend_urls import redirect_result_page

urlpatterns = [
    path('', RedirectView.as_view(url=settings.SITE_URL+'/ui/home/')),
    path('django/', include('validator.urls')),
    path('api/', include('api.urls')),
    # redirection to the new result page, it is needed for old published validations
    path('result/<uuid:result_uuid>/', redirect_result_page),
]
