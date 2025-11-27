
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