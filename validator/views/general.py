from django.shortcuts import render
from validator.models import Settings


def home(request):
    return render(request, 'validator/index.html', {'news_text': Settings.load().news})

def alpha(request):
    return render(request, 'validator/alpha.html')

def terms(request):
    return render(request, 'validator/terms.html')
