from django.shortcuts import redirect
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import logout
from validator.mailer import send_user_status_changed,send_user_account_removal_request
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth.decorators import login_required
from validator.forms.user_profile import UserProfileForm


@login_required(login_url='/login/')
def user_profile(request):
    
    if request.method == 'POST':
        print('User profile submit')
        form = UserProfileForm(request.POST,instance=request.user)
        if form.is_valid():
            current_password_hash=request.user.password
            newuser = form.save(commit=False)
            
            if form.cleaned_data['password1']=='':
                newuser.password=current_password_hash
                
            newuser.save()
            update_session_auth_hash(request, newuser)
            return redirect('user_profile_updated')
            
        return render(request, 'user/profile.html', {'form': form,})
    
    elif request.method == 'DELETE':
        request.user.is_active= False
        request.user.save()
        send_user_account_removal_request(request.user)
        send_user_status_changed(request.user,False)
        logout(request)
        return HttpResponse(status=200)
        
    else:
        if isinstance(request.user, AnonymousUser) == False:
            form = UserProfileForm( initial={ 'first_name':request.user.first_name, 
                                             'last_name':request.user.last_name, 
                                             'organisation': request.user.organisation, 
                                             'username': request.user.username, 
                                             'country': request.user.country,
                                             'email':request.user.email})
        else:
            form = UserProfileForm()

    return render(request, 'user/profile.html', {'form': form,})
    
@login_required(login_url='/login/')
def user_profile_updated(request):
    return render(request, 'user/profile_updated.html')

def user_profile_deactivated(request):
    return render(request, 'user/profile_deactivated.html')
