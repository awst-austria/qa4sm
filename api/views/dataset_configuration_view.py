from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer

from validator.models import DatasetConfiguration
# imported from depths rather than from validation, which would drag pytesmo
# and the whole validation stack into an API view for two short strings
from validator.validation.depths import depth_label, merged_unit


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_configuration(request):
    configs = DatasetConfiguration.objects.all()
    serializer = ConfigurationSerializer(configs, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def dataset_configuration_by_validation(request, **kwargs):
    configs = DatasetConfiguration.objects.filter(validation_id=kwargs['validation_id'])
    serializer = ConfigurationSerializer(configs, many=True)

    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


class ConfigurationSerializer(ModelSerializer):
    """
    Serves the configuration behind a finished validation.

    The three merge fields are computed, not stored. Resolving `variable`
    against the DataVariable table gives the wrong answer for a merged run:
    the stored variable is only the shallowest contributing layer, and for
    GLDAS its unit is the raw kg/m² rather than the m³/m³ the merged series
    actually holds. Clients should take the unit from here rather than looking
    it up themselves.

    A configuration that does not merge reports an empty layer list, a blank
    depth label and its variable's own unit — exactly what a client computed
    before these fields existed, so nothing about existing validations changes.
    """

    variable_unit = serializers.SerializerMethodField()
    merged_layers = serializers.SerializerMethodField()
    merge_depth_label = serializers.SerializerMethodField()

    def _merged_layers(self, obj):
        # the model property queries on every access and three fields need it
        if not hasattr(obj, '_merged_layers_cache'):
            obj._merged_layers_cache = obj.merged_layers
        return obj._merged_layers_cache

    def get_variable_unit(self, obj) -> str:
        merged = self._merged_layers(obj)
        if not merged:
            return obj.variable.unit
        return merged_unit(merged, obj.variable.unit)

    def get_merged_layers(self, obj) -> list:
        return [{'id': layer.id,
                 'short_name': layer.short_name,
                 'depth_from': layer.depth_from,
                 'depth_to': layer.depth_to}
                for layer in self._merged_layers(obj)]

    def get_merge_depth_label(self, obj) -> str:
        merged = self._merged_layers(obj)
        return depth_label(merged) if merged else ''

    class Meta:
        model = DatasetConfiguration
        fields = ['id',
                  'validation',
                  'dataset',
                  'version',
                  'variable',
                  'filters',
                  'parametrised_filters',
                  'parametrisedfilter_set',
                  'is_spatial_reference',
                  'is_temporal_reference',
                  'is_scaling_reference',
                  'merge_weighted',
                  'variable_unit',
                  'merged_layers',
                  'merge_depth_label']
