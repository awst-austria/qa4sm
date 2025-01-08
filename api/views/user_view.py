from django.contrib.auth import logout
from django.http import HttpResponse, QueryDict, JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from validator.forms import SignUpForm, UserProfileForm
from validator.mailer import send_new_user_signed_up, send_user_account_removal_request, send_user_status_changed
from django.contrib.auth import update_session_auth_hash


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
        newuser = form.save(commit=False)

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def password_update(request):
    serializer = PasswordUpdateSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        # Verify the old password
        if not user.check_password(serializer.validated_data['old_password']):
            return JsonResponse(
                {
                    'error': "The old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return JsonResponse({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
    else:
        full_error = ''
        for error in serializer.errors['non_field_errors']:
            full_error += f'{error}\n\n'
        return JsonResponse({'error': full_error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    request.user.is_active = False
    request.user.save()
    send_user_account_removal_request(request.user)
    send_user_status_changed(request.user, False)
    logout(request)
    return HttpResponse(status=200)


class PasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Ensure new_password matches confirm_password
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Validate the new password using Django's password validators
        password_validation.validate_password(attrs['new_password'])

        return attrs
