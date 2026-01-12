# interactive_map_view.py
import os
import numpy as np
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from .interactive_map_utils import get_transparent_tile, compute_norm_params, get_layernames, get_colormap_metadata, get_spread_and_buffer, get_colormap, get_cached_dataframe_with_index, build_status_legend_data, get_point_value
import io
from pyproj import Transformer
from PIL import Image
import json
import morecantile
import datashader as ds
import datashader.transfer_functions as tf
import zarr
from ..services.interactive_map_service import get_plot_resolution, get_cached_zarr_path, get_common_unit, check_zarr_file_exists
from validator.validation.globals import QR_STATUS_DICT, QR_VALUE_RANGES


# Cache TMS and transformer objects 
TMS_4326 = morecantile.tms.get("WorldCRS84Quad")  # EPSG:4326
TMS_3857 = morecantile.tms.get("WebMercatorQuad")  # EPSG:3857
TRANSFORMER_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)



@require_http_methods(["GET"])
def check_zarr_exists(request, validation_id):
    """API endpoint to check if zarr file exists"""
    exists = check_zarr_file_exists(validation_id)
    return JsonResponse({'exists': exists})


@require_http_methods(["GET"])
def get_data_point(request, validation_id, metric_name, layer_name):
    try:
        x = float(request.GET.get('x'))
        y = float(request.GET.get('y'))
        z = float(request.GET.get('z'))
        projection = int(request.GET.get('projection', 4326))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)

    zarr_path = get_cached_zarr_path(validation_id)

    return get_point_value(request, validation_id, layer_name, zarr_path, 
                          x, y, z, projection)


# API endpoints


@require_http_methods(["GET"])
def get_layer_bounds(request, validation_id):
    """Get geographic bounds from Zarr lat/lon arrays (same for all metrics)"""
    
    # Cache key only uses validation_id since bounds are the same for all metrics
    bounds_cache_key = f"bounds_{validation_id}"
    bounds_data = cache.get(bounds_cache_key)
    
    if not bounds_data:
        try:
            zarr_path = get_cached_zarr_path(validation_id)
            
            # Open the Zarr store
            store = zarr.open(zarr_path, mode='r')
            
            # Read lat/lon arrays
            if 'lat' not in store or 'lon' not in store:
                return JsonResponse(
                    {"error": "lat/lon arrays not found in Zarr store"}, 
                    status=404
                )
            
            lat = store['lat'][:]
            lon = store['lon'][:]
            
            # Filter out fill values (NaN) if present
            lat_valid = lat[~np.isnan(lat)]
            lon_valid = lon[~np.isnan(lon)]
            
            if len(lat_valid) == 0 or len(lon_valid) == 0:
                return JsonResponse(
                    {"error": "No valid coordinates found"}, 
                    status=404
                )
            
            # Calculate bounds
            min_lon = float(np.min(lon_valid))
            max_lon = float(np.max(lon_valid))
            min_lat = float(np.min(lat_valid))
            max_lat = float(np.max(lat_valid))
            
            # Add a small buffer (1% of the range) to ensure all points are visible
            lon_buffer = (max_lon - min_lon) * 0.01 or 0.1
            lat_buffer = (max_lat - min_lat) * 0.01 or 0.1
            
            bounds_data = {
                'extent': [
                    min_lon - lon_buffer,
                    min_lat - lat_buffer,
                    max_lon + lon_buffer,
                    max_lat + lat_buffer
                ],
                'center': [
                    (min_lon + max_lon) / 2,
                    (min_lat + max_lat) / 2
                ],
                'num_points': len(lat_valid)
            }
            
            # Cache for longer (24 hours) since this never changes for a validation
            cache.set(bounds_cache_key, bounds_data, timeout=86400)
            
        except Exception as e:
            return JsonResponse(
                {"error": f"Error reading Zarr bounds: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse(bounds_data)



@require_http_methods(["GET"])
def get_layer_range(request, validation_id, metric_name, layer_name):
    """Get vmin/vmax for a specific layer, respecting constraints and categorical data"""

    range_cache_key = f"range_{validation_id}_{metric_name}_{layer_name}"
    range_data = cache.get(range_cache_key)

    if not range_data:
        # Special handling for status (categorical)
        if metric_name == 'status' or layer_name.startswith('status'):
            range_data = {
                'vmin': min(QR_STATUS_DICT.keys()),
                'vmax': max(QR_STATUS_DICT.keys()),
                'is_categorical': True,
                'categories': QR_STATUS_DICT,
                'num_colors': len(QR_STATUS_DICT)
            }
        else:
            # Continuous data - compute from actual data
            zarr_path = get_cached_zarr_path(validation_id)
            vmin, vmax = compute_norm_params(
                validation_id, 
                zarr_path,
                metric_name, 
                layer_name,
            )

            range_data = {
                'vmin': float(vmin),
                'vmax': float(vmax),
                'is_categorical': False,
                'has_constraints': metric_name in QR_VALUE_RANGES
            }

        # Cache for 2 hours
        cache.set(range_cache_key, range_data, timeout=7200)

    return JsonResponse(range_data)




@require_http_methods(["POST"])
def get_validation_layer_metadata(request, validation_id):
    """Fetch metadata including layer mappings, gradients, and status legends (NO vmin/vmax)"""
    def convert_numpy(obj):
        """Recursively convert numpy types to native Python types"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: convert_numpy(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_numpy(item) for item in obj]
        return obj

    cache_key = f"layer_metadata_{validation_id}"
    metadata = cache.get(cache_key)

    if not metadata:
        data = json.loads(request.body)
        possible_layers = data.get('possible_layers', {})

        zarr_path = get_cached_zarr_path(validation_id)
        available_layers_mapping = get_layernames(zarr_path)
        unit = get_common_unit(validation_id)
        layers = []
        status_metadata = {}

        for metric, possible_layer_list in possible_layers.items():
            for possible_layer_name in possible_layer_list:
                if possible_layer_name in available_layers_mapping.values():
                    colormap_info = get_colormap_metadata(metric)

                    layers.append({
                        'name': possible_layer_name,
                        'metric': metric,
                        'colormap': colormap_info
                    })

                    # Handle status legends with actual values
                    if metric == 'status':
                        status_legend = build_status_legend_data(
                            colormap_info,
                            zarr_path,
                            possible_layer_name
                        )
                        status_metadata[possible_layer_name] = status_legend

        metadata = {
            'validation_id': validation_id, 
            'layers': layers,
            'status_metadata': status_metadata,
            'unit' : unit,
        }

        cache.set(cache_key, metadata, timeout=3600)

    # Convert numpy arrays to native Python types
    metadata = convert_numpy(metadata)

    return JsonResponse(metadata)






    
@require_http_methods(["GET"])
def get_tile(request, validation_id, metric_name, layer_name, projection, z, x, y):
    """Serve a datashader tile with efficient DataFrame caching."""

    if projection not in (4326, 3857):
        return HttpResponse("Invalid projection. Use '4326' or '3857'", status=400)

    zarr_path = get_cached_zarr_path(validation_id)

    if zarr_path is None or not os.path.exists(zarr_path):
        return HttpResponse(status=404)

    try:
        df, tree, coord_cols = get_cached_dataframe_with_index(
            validation_id, layer_name, zarr_path, projection
        )

        if df is None or len(df) == 0:
            return get_transparent_tile()

        # Select TMS and get tile bounds
        tms = TMS_3857 if projection == 3857 else TMS_4326
        bbox = tms.xy_bounds(x, y, z)

        # Get spread parameters based on data distribution
        resolution = get_plot_resolution(validation_id)
        is_scattered = resolution['is_scattered']

        if is_scattered:
            spread_px, buffer_px, marker_shape = 8, 9, 'circle'
        else:
            spread_px, buffer_px = get_spread_and_buffer(validation_id, z, resolution['plot_resolution'])
            marker_shape = 'square'

        # Calculate ranges and buffers
        x_range = bbox.right - bbox.left
        y_range = bbox.top - bbox.bottom
        x_buffer = x_range * (buffer_px / 256)
        y_buffer = y_range * (buffer_px / 256)

        # Buffered bounds
        x_min, x_max = bbox.left - x_buffer, bbox.right + x_buffer
        y_min, y_max = bbox.bottom - y_buffer, bbox.top + y_buffer

        # Filter data with buffered bounds
        col_x, col_y = coord_cols
        mask = ((df[col_x] >= x_min) & (df[col_x] <= x_max) &
                (df[col_y] >= y_min) & (df[col_y] <= y_max))
        df_tile = df[mask].copy()

        if len(df_tile) == 0:
            return get_transparent_tile()

        # Map to buffered pixel space
        buffered_size = 256 + 2 * buffer_px
        df_tile['px'] = (df_tile[col_x] - x_min) / (x_range + 2 * x_buffer) * buffered_size
        df_tile['py'] = (df_tile[col_y] - y_min) / (y_range + 2 * y_buffer) * buffered_size

        # Create buffered canvas
        cvs = ds.Canvas(
            plot_width=buffered_size,
            plot_height=buffered_size,
            x_range=(0, buffered_size),
            y_range=(0, buffered_size)
        )

        # Get normalization parameters and colormap
        vmin, vmax = compute_norm_params(validation_id, zarr_path, metric_name, layer_name)
        mpl_cmap = get_colormap(metric_name)

        # Aggregate and shade based on data type
        is_categorical = metric_name == 'status' or layer_name.startswith('status')
        agg = cvs.points(df_tile, 'px', 'py', agg=ds.first('value') if is_categorical else ds.mean('value'))

        if is_categorical:
            status_codes = sorted(QR_STATUS_DICT.keys())
            colors_hex = [
                '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
                for r, g, b, a in (mpl_cmap(i) for i in range(len(status_codes)))
            ]
            color_key = {int(code): colors_hex[i] for i, code in enumerate(status_codes)}
            img = tf.shade(agg, color_key=color_key, how='linear')
        else:
            img = tf.shade(agg, cmap=mpl_cmap, how='linear', span=(vmin, vmax))

        # Create black halo layer and colored marker layer, then stack
        img_halo = tf.spread(tf.shade(agg, cmap=['black'], how='linear'), px=spread_px + 1, shape=marker_shape)
        img = tf.stack(img_halo, tf.spread(img, px=spread_px, shape=marker_shape))

        # Crop to tile bounds and output
        pil_img = img.to_pil().convert('RGBA')
        pil_img = pil_img.crop((buffer_px, buffer_px, 256 + buffer_px, 256 + buffer_px))

        img_buffer = io.BytesIO()
        pil_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return HttpResponse(img_buffer.getvalue(), content_type='image/png')

    except Exception as e:
        print(f"Error generating tile: {e}")
        import traceback
        traceback.print_exc()
        return get_transparent_tile()

