from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from validator.models import UserDatasetFile


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_of_user_data_files(request):
    list_of_files = UserDatasetFile.objects.filter(owner=request.user)
    serializer = UploadSerializer(list_of_files, many=True)
    return JsonResponse(serializer.data, status=200, safe=False)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_dataset(request, dataset_id):
    dataset = get_object_or_404(UserDatasetFile, pk=dataset_id)

    if dataset.owner != request.user:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    dataset.delete()

    return HttpResponse(status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FileUploadParser])
def upload_user_data(request, filename):
    file = request.FILES['file']
    file_owner = request.user

    file_data = {
        'file': file,
        'owner': file_owner.pk,
        'file_name': filename,
        'dataset': 1,
        'version': 1,
        'variable': 1
    }

    file_serializer = UploadSerializer(data=file_data)
    if file_serializer.is_valid():
        new_file = file_serializer.save()
        new_file.save()

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

