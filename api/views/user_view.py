from django.contrib.auth import logout
from django.http import HttpResponse, QueryDict, JsonResponse
from django.middleware.csrf import get_token
from django_countries.serializer_fields import CountryField
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import DateTimeField, CharField
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from validator.forms import SignUpForm, UserProfileForm
from validator.mailer import send_new_user_signed_up, send_user_account_removal_request, send_user_status_changed
from validator.models import User
from django.contrib.auth import update_session_auth_hash
from rest_framework.authtoken.models import Token


def _get_querydict_from_user_data(request, userdata):
    user_data_dict = QueryDict(mutable=True)
    user_data_dict.update({'csrfmiddlewaretoken': get_token(request)})
    user_data_dict.update(userdata)
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
        if form.cleaned_data['password1'] == '':
            newuser.password = current_password_hash

        newuser.save()
        update_session_auth_hash(request, newuser)
        keys_to_remove = ['password1', 'password2', 'csrfmiddlewaretoken', 'terms_consent']
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_token(request):
    token_list = Token.objects.filter(user=request.user)
    token = token_list[0].key if len(token_list) else None
    response = {'token': token, 'exists': token is not None}
    return JsonResponse(response, status=200)


class UserSerializer(ModelSerializer):
    last_login = DateTimeField(read_only=True)
    date_joined = DateTimeField(read_only=True)
    password = CharField(write_only=True)
    country = CountryField()

    class Meta:
        model = User
        fields = ['username',
                  'password',
                  'email',
                  'first_name',
                  'last_name',
                  'organisation',
                  'last_login',
                  'date_joined',
                  'country',
                  'orcid',
                  'id',
                  'copied_runs',
                  'space_limit',
                  'space_limit_value',
                  'space_left',
                  'is_staff',
                  'is_superuser']
