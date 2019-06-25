from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from validator.forms import SignUpForm
from validator.mailer import send_new_user_signed_up
from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.decorators import login_required
from validator.forms.user_profile import UserProfileForm


@login_required(login_url='/login/')
def user_profile(request):
    
    if request.method == 'POST':
        if request.user != None:
            print('Current user: '+request.user.username+' pass: '+request.user.password)
        form = UserProfileForm(request.POST,instance=request.user)
        if form.is_valid():
            current_password_hash=request.user.password
            newuser = form.save(commit=False)
            
            if form.cleaned_data['password1']=='':
                newuser.password=current_password_hash
                
            newuser.save()
            messages.success(request, 'Your password was successfully updated!')
            
        return render(request, 'user/profile.html', {'form': form,})
    else:
        if isinstance(request.user, AnonymousUser) == False:
            print('Current user: '+request.user.username)
            # {'charfield1': 'foo', 'charfield2': 'bar'}
            form = UserProfileForm( initial={ 'first_name':request.user.first_name, 'last_name':request.user.last_name, 'organisation': request.user.organisation, 'username': request.user.username, 'country': request.user.country,'email':request.user.email})
        else:
            form = UserProfileForm()

    return render(request, 'user/profile.html', {'form': form,})

def signup_complete(request):
    return render(request, 'auth/signup_complete.html')
