from django.shortcuts import redirect
from django.shortcuts import render

from validator.forms import SignUpForm
from validator.mailer import send_new_user_signed_up


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            newuser = form.save(commit=False)
            # new user should not be active by default, admin needs to confirm
            newuser.is_active = False
            newuser.save()

            # notify the admins
            send_new_user_signed_up(newuser)

            return redirect('signup_complete')
    else:
        form = SignUpForm()

    return render(request, 'validator/signup.html', {'form': form})

def signup_complete(request):
    return render(request, 'validator/signup_complete.html')
