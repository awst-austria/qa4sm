from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from validator.models import DatasetVersion

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_version(request):
    # dataset_id = request.query_params.get('dataset', None)
    # datasets = []
    # # get single dataset
    # if dataset_id:
    #     pass
    # # get all datasets
    # else:
    #     pass
    #
    # if request.user.is_superuser:
    #     print('super')

    datasets = DatasetVersion.objects.all()
    serializer = DatasetSerializer(datasets, many=True)
    #
    # print(serializer.data)
    # json = JSONRenderer().render(serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)


class DatasetSerializer(ModelSerializer):
    class Meta:
        model = DatasetVersion
        fields = ['id',
                  'short_name',
                  'pretty_name',
                  'help_text',
                  'storage_path',
                  'detailed_description',
                  'source_reference',
                  'citation',
                  'is_only_reference',
                  'versions',
                  'variables',
                  'filters',
                  ]
