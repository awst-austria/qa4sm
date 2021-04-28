from django.http import JsonResponse

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated

from validator.models import ValidationRun
from api.views.auxiliary_functions import get_fields_as_list

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eligible_results(request):
    val_runs = ValidationRun.objects.all()
    current_user = request.user
    user_only = request.query_params.get('user_only', None)  # todo: user_only to get only the validations belonging to user
    reference_ds = request.query_params.get('reference', None)

    if user_only:
        val_runs = ValidationRun.objects.filter(user=current_user)
    else:
        val_runs = ValidationRun.objects.all()


    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
