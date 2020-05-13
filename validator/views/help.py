from django.shortcuts import render
from django.conf import settings

def userhelp(request):
    context = {
        'expiry_period' : settings.VALIDATION_EXPIRY_DAYS,
        'warning_period' : settings.VALIDATION_EXPIRY_WARNING_DAYS,
        }
    return render(request, 'validator/help.html', context)
