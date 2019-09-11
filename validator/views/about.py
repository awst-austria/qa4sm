from django.shortcuts import render
from valentina.settings import APP_VERSION

def about(request):
    return render(request, 'validator/about.html',{'app_version' : APP_VERSION})