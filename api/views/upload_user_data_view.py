from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import UserDatasetFile


@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    file = request.FILES['file']
    file_owner = request.user

    file_data = {
        'file': file,
        'owner': file_owner.pk,
        'file_name': filename
    }

    file_serializer = UploadSerializer(data=file_data)
    if file_serializer.is_valid():
        file_serializer.save()

        print('i am the king of the world')
    else:
        print('you suck')
        print(file_serializer.errors)

    return JsonResponse(file_serializer.data, status=200, safe=False)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([FileUploadParser])
# def validate_user_data(request, format=None):
#     serializer_class = UploadSerializer
#     print(dir(request.FILES), request.FILES.keys(), request.data)
#     response = {'message': 'Monika'}
#     return JsonResponse(response, status=200, safe=False)


class UploadSerializer(ModelSerializer):
    class Meta:
        model = UserDatasetFile
        fields = '__all__'



class FileSerializer(ModelSerializer):
    class Meta:
        model = UserDatasetFile
        fields = '__all__'
