from django.shortcuts import render


def home(request):
    return render(request, 'validator/index.html')

def alpha(request):
    return render(request, 'validator/alpha.html')

def terms(request):
    return render(request, 'validator/terms.html')
