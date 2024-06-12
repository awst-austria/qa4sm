from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from valentina.settings_conf import EMAIL_HOST_USER

from validator.mailer import send_user_help_request


@api_view(['POST'])
@permission_classes([AllowAny])
def send_support_request(request):
    user_name, user_email, message, send_copy_to_user, is_active, slider = request.data.values()
    if is_active or slider == 0:
        return JsonResponse({"message": 'Sorry, looks like you are not a real person.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        send_user_help_request(user_name, user_email, message, send_copy_to_user)
        return JsonResponse({'message': 'Ok'}, status=status.HTTP_200_OK)
    except:
        return JsonResponse({
                                'message': f'Please try again later or send us email '
                                           f'directly to {EMAIL_HOST_USER}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
