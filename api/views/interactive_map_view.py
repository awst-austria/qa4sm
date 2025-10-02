# interactive_map_view.py
import os
import numpy as np
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from collections import defaultdict
from django.http import JsonResponse, HttpResponse
from rio_tiler.io import COGReader  # works for Cloud Optimized GeoTIFFs, but works for standard TIFFs too
from rio_tiler.errors import TileOutsideBounds
import io
from PIL import Image
from rio_tiler.colormap import cmap
import matplotlib.cm as cm
import rasterio
import json
from validator.validation.globals import QR_COLORMAPS, QR_STATUS_DICT


# UTILS AND COLORMAP

def get_cache_key(validation_id, band_index):
    """Generate consistent cache keys"""
    return f"validation_{validation_id}_{band_index}"

def create_transparent_tile():
    """Create a transparent 256x256 PNG tile"""
    # Create a transparent image
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))

    # Save to buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return HttpResponse(img_buffer.getvalue(), content_type='image/png')


def get_colormap(metric_name):
    """Get cached colormap for a specific metric"""
    cache_key = f"colormap_{metric_name}"
    cached_colormap = cache.get(cache_key)
    
    #if cached_colormap:
    #    return cached_colormap
    
    try:
        # Get the matplotlib colormap from QR_COLORMAPS
        if metric_name in QR_COLORMAPS:
            mpl_colormap = QR_COLORMAPS[metric_name]
        else:
            # Fallback to a default colormap if metric not found
            mpl_colormap = cm.get_cmap('viridis')  # or whatever default you prefer
        
        # Cache for 24 hours (colormaps don't change)
        cache.set(cache_key, mpl_colormap, 86400)
        return mpl_colormap
    
    except Exception as e:
        print(f"Error getting colormap for metric {metric_name}: {e}")
        # Return a safe default colormap
        return cm.get_cmap('viridis')


def get_colormap_type(mpl_colormap):
    """Get information about the colormap type and properties"""
    if hasattr(mpl_colormap, 'colors') and hasattr(mpl_colormap, 'N'):
        return {
            'type': 'ListedColormap',
            'num_colors': mpl_colormap.N,
            'colors': mpl_colormap.colors
        }
    else:
        return {
            'type': 'LinearSegmentedColormap',
            'name': getattr(mpl_colormap, 'name', 'unknown')
        }


def generate_css_gradient(mpl_colormap, metric_name=None, num_colors=10):
    """Convert matplotlib colormap to CSS gradient string"""
    try:
        # Get colormap information
        colormap_info = get_colormap_type(mpl_colormap)
        
        if colormap_info['type'] == 'ListedColormap':
            # For ListedColormap, use the actual discrete colors
            colors = []
            actual_colors = colormap_info['colors']
            
            for rgba in actual_colors:
                # Convert to CSS rgba format
                css_color = f"rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3] if len(rgba) > 3 else 1.0})"
                colors.append(css_color)
            
            # For categorical data like 'status', create equal segments
            if metric_name == 'status' and len(colors) > 1:
                # Create discrete segments with equal width for categorical data
                segment_width = 100 / len(colors)
                gradient_parts = []
                
                for i, color in enumerate(colors):
                    start_pos = i * segment_width
                    end_pos = (i + 1) * segment_width
                    
                    # Create sharp transitions between categories
                    gradient_parts.append(f"{color} {start_pos}%")
                    gradient_parts.append(f"{color} {end_pos}%")
                
                gradient = f"linear-gradient(to right, {', '.join(gradient_parts)})"
            elif len(colors) > 1:
                # For other discrete colormaps, still create segments but maybe smoother
                segment_width = 100 / len(colors)
                gradient_parts = []
                
                for i, color in enumerate(colors):
                    start_pos = i * segment_width
                    end_pos = (i + 1) * segment_width
                    
                    if i == 0:
                        gradient_parts.append(f"{color} {start_pos}%")
                    
                    gradient_parts.append(f"{color} {end_pos}%")
                
                gradient = f"linear-gradient(to right, {', '.join(gradient_parts)})"
            else:
                # Single color case
                gradient = f"linear-gradient(to right, {colors[0]}, {colors[0]})"
                
        else:
            # For LinearSegmentedColormap, sample colors continuously
            colors = []
            for i in range(num_colors):
                # Sample from 0 to 1
                normalized_pos = i / (num_colors - 1)
                rgba = mpl_colormap(normalized_pos)
                # Convert to CSS rgba format
                css_color = f"rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3] if len(rgba) > 3 else 1.0})"
                colors.append(css_color)
            
            # Create smooth CSS linear gradient
            gradient = f"linear-gradient(to right, {', '.join(colors)})"
        
        return gradient
    
    except Exception as e:
        print(f"Error generating CSS gradient: {e}")
        return "linear-gradient(to right, blue, cyan, yellow, red)"  # fallback
    

def get_colormap_metadata(metric_name):
    """Get static colormap metadata (gradient, type, categories) - NO file I/O"""
    cache_key = f"colormap_metadata_{metric_name}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    # Get the colormap for this metric
    colormap = get_colormap(metric_name)
    colormap_info = get_colormap_type(colormap)

    # Generate CSS gradient colors from the matplotlib colormap
    gradient_colors = generate_css_gradient(colormap, metric_name)

    result = {
        'gradient': gradient_colors,
        'is_categorical': metric_name == 'status',  # Adjust based on your logic
        'colormap_info': colormap_info
    }

    # Add category definitions for status
    if metric_name == 'status':
        result['categories'] = QR_STATUS_DICT

    # Cache indefinitely - this never changes
    cache.set(cache_key, result, None)

    return result


# GEOTIFF ACCESS


def get_validation_data(request, validation_id):
    """Get validation data with session fallback"""
    # 1. Try session storage
    session_key = f"validation_{validation_id}"
    #if session_key in request.session:
    #    return request.session[session_key]

    # 2. Database fallback
    try:
        from validator.models import ValidationRun

        validation_run = ValidationRun.objects.get(id=validation_id)

        # Convert relative path to absolute path immediately
        absolute_geotiff_path = os.path.join(settings.MEDIA_ROOT, validation_run.geotiff_path)

        data = {
            'geotiff_path': absolute_geotiff_path,
        }

        # Store in session for future requests
        request.session[session_key] = data
        return data

    except ValidationRun.DoesNotExist:
        return None


def get_layernames_and_indices(geotiff_path):
    """Get information about all bands in the GeoTIFF"""
    cache_key = f"dataset_info_{geotiff_path}"
    cached_info = cache.get(cache_key)

    if cached_info:
        return cached_info

    try:
        with rasterio.open(geotiff_path) as dataset:
            count = dataset.count
            descriptions = {}
            for i in range(1, count + 1):
                desc = dataset.descriptions[i - 1]
                if desc is not None:  # Only add if description exists
                    descriptions[str(i)] = desc

        # Cache for 1 hour
        cache.set(cache_key, descriptions, 3600)
        return descriptions

    except Exception as e:
        print(f"Error reading dataset info: {e}")
        return {}


def compute_norm_params(validation_id, geotiff_path, band_index):
    """Compute normalization parameters for a specific band"""
    cache_key = get_cache_key(validation_id, band_index)
    cached_params = cache.get(cache_key)

    if cached_params:
        return cached_params

    try:
        with rasterio.open(geotiff_path) as dataset:
            band_data = dataset.read(band_index, masked=True)
            vmin = float(np.nanmin(band_data))
            vmax = float(np.nanmax(band_data))

        # Cache for 24 hours (longer since this is expensive)
        cache.set(cache_key, (vmin, vmax), 86400)
        return vmin, vmax

    except Exception as e:
        print(f"Error computing normalization parameters: {e}")
        return 0.0, 1.0



@require_http_methods(["GET"])
def get_pixel_value(request):
    return 1


# LEGEND 

def get_status_legend_data(geotiff_path, band_index):
    """Get status legend data by reading unique values from the GeoTIFF"""
    cache_key = f"status_legend_{geotiff_path}_{band_index}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    try:
        with rasterio.open(geotiff_path) as dataset:
            # Read the band data
            band_data = dataset.read(band_index, masked=True)

            # Get unique values, excluding NaN/masked values
            unique_values = np.unique(band_data.compressed())
            unique_values = unique_values[~np.isnan(unique_values)]
            unique_values = sorted([int(val) for val in unique_values if not np.isnan(val)])

        # Get the colormap for status
        status_colormap = get_colormap('status')
        colormap_info = get_colormap_type(status_colormap)

        # Create legend entries for each unique status value found in the data
        legend_entries = []

        for status_value in unique_values:
            if status_value in QR_STATUS_DICT:
                # Map status value to colormap index (shift by 1: -1→0, 0→1, etc.)
                colormap_index = status_value + 1

                if colormap_info['type'] == 'ListedColormap' and colormap_index < len(colormap_info['colors']):
                    rgba = colormap_info['colors'][colormap_index]
                    # Convert to hex color for frontend
                    hex_color = f"#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}"

                    legend_entries.append({
                        'value': status_value,
                        'label': QR_STATUS_DICT[status_value],
                        'color': hex_color,
                        'rgba': rgba
                    })

        legend_data = {
            'type': 'categorical',
            'entries': legend_entries,
            'total_categories': len(QR_STATUS_DICT)
        }

        # Cache for 1 hour
        cache.set(cache_key, legend_data, 3600)
        return legend_data

    except Exception as e:
        print(f"Error getting status legend data: {e}")
        return {
            'type': 'categorical',
            'entries': [],
            'total_categories': len(QR_STATUS_DICT)
        }


# API endpoints

@require_http_methods(["GET"])
def get_layer_range(request, validation_id, metric_name, index):
    """Get vmin/vmax for a specific layer by index (lazy-loaded)"""

    # Cache key for this specific layer's range
    range_cache_key = f"range_{validation_id}_{metric_name}_{index}"
    range_data = cache.get(range_cache_key)

    #if not range_data:
    if True:
        geotiff_path = get_validation_data(request, validation_id)

        # Special handling for categorical data
        if metric_name == 'status':
            # Get metadata to access colormap info
            metadata_cache_key = f"layer_metadata_{validation_id}"
            metadata = cache.get(metadata_cache_key)

            if metadata:
                colormap_metadata = metadata.get('colormap_metadata', {}).get(metric_name, {})
                colormap_info = colormap_metadata.get('colormap_info', {})

                if colormap_info.get('type') == 'ListedColormap':
                    vmin = 0
                    vmax = colormap_info.get('num_colors', 1) - 1
                else:
                    vmin, vmax = compute_norm_params(
                        validation_id, 
                        geotiff_path['geotiff_path'], 
                        index
                    )
            else:
                # Fallback if metadata not cached
                vmin, vmax = compute_norm_params(
                    validation_id, 
                    geotiff_path['geotiff_path'], 
                    index
                )

            range_data = {
                'vmin': vmin,
                'vmax': vmax
            }
        else:
            # Continuous data - compute from GeoTIFF
            vmin, vmax = compute_norm_params(
                validation_id, 
                geotiff_path['geotiff_path'], 
                index
            )

            range_data = {
                'vmin': vmin,
                'vmax': vmax
            }

        # Cache for 2 hours (longer than metadata)
        cache.set(range_cache_key, range_data, timeout=7200)

    return JsonResponse(range_data)



@require_http_methods(["POST"])
def get_validation_layer_metadata(request, validation_id):
    """Fetch metadata including layer mappings, gradients, and status legends (NO vmin/vmax)"""
    cache_key = f"layer_metadata_{validation_id}"
    metadata = cache.get(cache_key)

    if not metadata:
        data = json.loads(request.body)
        possible_layers = data.get('possible_layers', {})

        geotiff_path = get_validation_data(request, validation_id)
        available_layers_mapping = get_layernames_and_indices(geotiff_path['geotiff_path'])

        # Create filtered mapping of only used layers: name -> index
        filtered_layer_mapping = defaultdict(dict)
        status_metadata = {}
        colormap_metadata = {}

        for metric, possible_layer_list in possible_layers.items():
            # Get colormap metadata for this metric (gradient, type, etc.)
            colormap_metadata[metric] = get_colormap_metadata(metric)

            for possible_layer_name in possible_layer_list:
                if match := next(((idx, desc) for idx, desc in available_layers_mapping.items()
                                if possible_layer_name == desc), None):
                    filtered_layer_mapping[metric][match[1]] = match[0]

                    # If this is a status metric, get the legend data (which values exist)
                    if metric == 'status':
                        band_index = int(match[0])
                        status_legend = get_status_legend_data(
                            geotiff_path['geotiff_path'], 
                            band_index
                        )
                        status_metadata[match[1]] = status_legend

        metadata = {
            'validation_id': validation_id, 
            'layer_mapping': filtered_layer_mapping,
            'colormap_metadata': colormap_metadata,  # Gradients and colormap info
            'status_metadata': status_metadata  # Which status values exist per layer
        }

        cache.set(cache_key, metadata, timeout=3600)

    return JsonResponse(metadata)



def get_colorbar_data(request, validation_id, metric_name, index):
    """Get all colorbar data: colormap, min/max values, and gradient colors"""

    geotiff_path = get_validation_data(request, validation_id)

    # Get the colormap for this metric
    colormap = get_colormap(metric_name)

    # Special handling for categorical data like 'status'
    if metric_name == 'status':
        # Get status-specific legend data
        status_legend = get_status_legend_data(geotiff_path['geotiff_path'], index)

        # For status data, use fixed limits based on the number of categories
        colormap_info = get_colormap_type(colormap)

        if colormap_info['type'] == 'ListedColormap':
            vmin = 0
            vmax = colormap_info['num_colors'] - 1
        else:
            vmin, vmax = compute_norm_params(validation_id, geotiff_path['geotiff_path'], index)

        # Generate CSS gradient colors from the matplotlib colormap
        gradient_colors = generate_css_gradient(colormap, metric_name)

        return {
            'vmin': vmin,
            'vmax': vmax,
            'gradient': gradient_colors,
            'metric_name': metric_name,
            'is_categorical': True,
            'legend_data': status_legend  # Include the legend data
        }
    else:
        # Get the min/max values for continuous data
        vmin, vmax = compute_norm_params(validation_id, geotiff_path['geotiff_path'], index)

        # Generate CSS gradient colors from the matplotlib colormap
        gradient_colors = generate_css_gradient(colormap, metric_name)

        return {
            'vmin': vmin,
            'vmax': vmax,
            'gradient': gradient_colors,
            'metric_name': metric_name,
            'is_categorical': False
        }

    
@require_http_methods(["GET"])
def get_tile(request, validation_id, metric_name, index, z, x, y):
    """Serve a tile for a specific validation run"""

    # Get validation data from cache
    validation_data = get_validation_data(request, validation_id)
    if validation_data is None:
        return HttpResponse(status=404)

    geotiff_path = validation_data['geotiff_path']

    # Check if file exists
    if not os.path.exists(geotiff_path):
        return HttpResponse(status=404)

    # Get dataset info to validate index
    layers = get_layernames_and_indices(geotiff_path)

    mpl_cmap = get_colormap(metric_name)


    if index < 1 or index > len(layers):
        return HttpResponse(status=404)

    try:
        # Get the normalization parameters for this index
        vmin, vmax = compute_norm_params(validation_id, geotiff_path, index)
        
        # Open the GeoTIFF and extract the tile
        with COGReader(geotiff_path) as cog:
            tile_data, mask = cog.tile(x, y, z, tilesize=256, indexes=index)
            
            # Remove the band dimension since we're dealing with a single band
            tile_data = tile_data.squeeze(axis=0)
            
            # Use the mask to set invalid pixels to NaN
            tile_data[mask == 0] = np.nan  # Assumes mask==0 means invalid data
            
            if metric_name == 'status':
                # For categorical status data, don't normalize - use raw integer values
                # The values should directly correspond to colormap indices
                colormap_info = get_colormap_type(mpl_cmap)
                
                if colormap_info['type'] == 'ListedColormap':
                    # Map data values (-1 to 8) to colormap indices (0 to 9)
                    # -1 (unforeseen) -> index 0, 0 (success) -> index 1, etc.
                    norm_data = tile_data + 1  # Shift: -1→0, 0→1, 1→2, ..., 8→9
                    
                    num_colors = colormap_info['num_colors']
                    norm_data = np.clip(norm_data, 0, num_colors - 1)
                    norm_data = norm_data / (num_colors - 1)
                else:
                    # Fallback normalization if status doesn't use ListedColormap
                    norm_data = (tile_data - vmin) / (vmax - vmin)
                    norm_data = np.clip(norm_data, 0, 1)
            else:
                # For continuous data, use regular normalization
                norm_data = (tile_data - vmin) / (vmax - vmin)
                norm_data = np.clip(norm_data, 0, 1)
            
            mpl_cmap.set_bad(color=(0, 0, 0, 0))  # transparent for NaN
            
            # Apply the colormap: this returns an RGBA image in float [0,1]
            rgba = mpl_cmap(norm_data)
            
            # Convert to 8-bit values and create the image
            img_data = (rgba * 255).astype(np.uint8)
            
            # Create a PIL Image from the RGBA array
            img = Image.fromarray(img_data)
            
            # Save the image to a bytes buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

        # Return the image as a response
        return HttpResponse(img_buffer.getvalue(), content_type='image/png')

    except TileOutsideBounds:
        # If the tile is outside the bounds of the dataset, return a transparent tile
        print('Tile outside bounds - returning transparent')
        return create_transparent_tile()

    except Exception as e:
        # Log the error and return a 500 error
        print(f"Error generating tile: {e}")
        return HttpResponse(status=500)

