from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from validator.models import ValidationRun
from api.views.auxiliary_functions import get_fields_as_list


@api_view(['GET'])
def published_results(request):

    val_runs = ValidationRun.objects.exclude(doi='')
    serializer = ResultsSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
def my_results(request):
    # toDO: val_runs should be filtered by user
    val_runs = ValidationRun.objects.all()
    serializer = ResultsSerializer(val_runs, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

class ResultsSerializer(ModelSerializer):
    class Meta:
        model = ValidationRun
        fields = get_fields_as_list(ValidationRun)

