
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404
from validator.models import ValidationRun, Dataset
import os
import math


def get_cached_zarr_path(validation_id):
    """Handles caching + model access for zarr paths"""
    cache_key = f'zarr_path_{validation_id}'
    zarr_path = cache.get(cache_key)

    if not zarr_path:
        validation_run = get_object_or_404(ValidationRun, id=validation_id)
        zarr_path = os.path.join(settings.MEDIA_ROOT, validation_run.zarr_path)
        cache.set(cache_key, zarr_path, timeout=3600)

    return zarr_path

def check_zarr_file_exists(validation_id):
    """Check if zarr.json exists in the validation's zarr path"""
    zarr_path = get_cached_zarr_path(validation_id)
    
    if not zarr_path:
        return False
    
    zarr_json = os.path.join(zarr_path, 'zarr.json')
    return os.path.isfile(zarr_json)

def get_plot_resolution(validation_id):
    """
    Retrieves plot resolution and related spatial reference metadata.
    
    Returns:
        dict: Contains 'plot_resolution' (float or None), 'is_scattered' (bool),
              and 'is_ismn' (bool)
    """
    cache_key = f'plot_resolution_{validation_id}'
    result = cache.get(cache_key)
    
    if not result:
        validation_run = get_object_or_404(ValidationRun, id=validation_id)
        dataset_id = validation_run.spatial_reference_configuration.dataset_id
        dataset = get_object_or_404(Dataset, id=dataset_id)
        
        plot_resolution = dataset.plot_resolution
        # Handle NaN - convert to None
        if plot_resolution is not None and math.isnan(plot_resolution):
            plot_resolution = None
        
        result = {
            'plot_resolution': plot_resolution,
            'is_scattered': dataset.is_scattered_data,
            'is_ismn': dataset.short_name == 'ISMN'
        }
        
        cache.set(cache_key, result, timeout=3600) 
    
    return result


def get_common_unit(validation_id):
    """
    Retrieves the common unit for a validation run.

    Returns:
        dict: Contains 'common_unit' (str or None) and 'from_scaling_ref' (bool)
    """
    cache_key = f'common_unit_{validation_id}'
    result = cache.get(cache_key)

    if result is not None:
        return result

    try:
        validation_run = get_object_or_404(ValidationRun, id=validation_id)

        # Priority 1: Use scaling_ref unit if available
        if validation_run.scaling_ref and validation_run.scaling_ref.variable:
            unit = validation_run.scaling_ref.variable.unit
            if unit:
                result = {'common_unit': unit, 'from_scaling_ref': True}
                cache.set(cache_key, result, timeout=3600)
                return result

        # Priority 2: Check all dataset configurations for common unit
        units = set()
        for config in validation_run.dataset_configurations.all():
            if config.variable and config.variable.unit:
                units.add(config.variable.unit)

        common_unit = units.pop() if len(units) == 1 else None

        result = {'common_unit': common_unit, 'from_scaling_ref': False}
        cache.set(cache_key, result, timeout=3600)
        return result

    except Exception:
        return {'common_unit': None, 'from_scaling_ref': False}

