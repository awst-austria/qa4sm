from django.contrib.auth import logout
from django.http import HttpResponse, QueryDict, JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from validator.forms import SignUpForm, UserProfileForm
from validator.mailer import send_new_user_signed_up, send_user_account_removal_request, send_user_status_changed
from django.contrib.auth import update_session_auth_hash



def _get_querydict_from_user_data(request, userdata):
    print(userdata)
    user_data_dict = QueryDict(mutable=True)
    user_data_dict.update({'csrfmiddlewaretoken': get_token(request)})
    user_data_dict.update(userdata)

    if not userdata.get('password1') and not userdata.get('password2'):
        # Optionally, you can skip the password fields entirely if they are not updated
        user_data_dict = user_data_dict.copy()  # Make it mutable again if it's not
        user_data_dict.pop('password1', None)
        user_data_dict.pop('password2', None)


    print(user_data_dict)
    return user_data_dict


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_post(request):
    new_user_data = _get_querydict_from_user_data(request, request.data)
    form = SignUpForm(new_user_data)
    if form.is_valid():
        if form.data.get('active') or form.data.get('honeypot') < 100:
            return JsonResponse({"message": ''}, status=status.HTTP_400_BAD_REQUEST)
        newuser = form.save(commit=False)
        # new user should not be active by default, admin needs to confirm
        newuser.is_active = False
        newuser.save()

        # notify the admins
        send_new_user_signed_up(newuser)
        response = JsonResponse({'response': 'New user registered'}, status=200)
    else:
        errors = form.errors.get_json_data()
        response = JsonResponse(errors, status=400, safe=False)

    return response


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def user_update(request):
    new_user_data = _get_querydict_from_user_data(request, request.data)
    form = UserProfileForm(new_user_data, instance=request.user)

    if form.is_valid():
        current_password_hash = request.user.password
        newuser = form.save(commit=False)
        if form.cleaned_data['password1'] == current_password_hash:
            newuser.password = current_password_hash

        newuser.save()
        update_session_auth_hash(request, newuser)
        keys_to_remove = ['csrfmiddlewaretoken', 'terms_consent']
        for key in keys_to_remove:
            del form.data[key]
        response = JsonResponse(form.data, status=200)
    else:
        errors = form.errors.get_json_data()
        response = JsonResponse(errors, status=400, safe=False)
    return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    request.user.is_active = False
    request.user.save()
    send_user_account_removal_request(request.user)
    send_user_status_changed(request.user, False)
    logout(request)
    return HttpResponse(status=200)

