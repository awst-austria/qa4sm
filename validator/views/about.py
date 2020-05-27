from django.shortcuts import render
from django.conf import settings

def about(request):
    return render(request, 'validator/about.html',{'app_version' : settings.APP_VERSION})