from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

from api.views.auxiliary_functions import get_fields_as_list
from validator.models import Settings


@api_view(['GET'])
@permission_classes([AllowAny])
def backend_settings(request):
    settings_model = Settings.objects.all()
    serializer = SettingsSerializer(settings_model, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK,
                        safe=False)


class SettingsSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = get_fields_as_list(model)
