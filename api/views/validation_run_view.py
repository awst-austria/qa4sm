from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import ValidationRun


@api_view(['GET'])
@permission_classes([AllowAny])
def published_results(request):

    limit = int(request.query_params.get('limit', None))
    offset = int(request.query_params.get('offset', None))
    order = request.query_params.get('order',None)

    val_runs = ValidationRun.objects.exclude(doi='').order_by(order)

    serializer = ValidationRunSerializer(val_runs[offset:(offset+limit)], many=True)
    response = {'validations': serializer.data,
                'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    current_user = request.user
    limit = int(request.query_params.get('limit', None))
    offset = int(request.query_params.get('offset', None))
    order = request.query_params.get('order', None)

    val_runs = ValidationRun.objects.filter(user=current_user).order_by(order)

    serializer = ValidationRunSerializer(val_runs[offset:(offset+limit)], many=True)
    response = {'validations': serializer.data, 'length': len(val_runs)}

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_runs(request, **kwargs):
    val_runs = ValidationRun.objects.all()
    serializer = ValidationRunSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validation_run_by_id(request, **kwargs):
    val_run = ValidationRun.objects.get(pk=kwargs['id'])
    if val_run is None:
        return JsonResponse(None, status=status.HTTP_404_NOT_FOUND, safe=False)

    serializer = ValidationRunSerializer(val_run)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ValidationRunSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(ValidationRun)
