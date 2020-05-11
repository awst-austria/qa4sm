from django.shortcuts import render
# from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'validator/index.html')

# @login_required(login_url='/login/')
def alpha(request):
    return render(request, 'validator/alpha.html')

# @login_required(login_url='/login/')
def userhelp(request):
    return render(request, 'validator/help.html')

def terms(request):
    return render(request, 'validator/terms.html')
