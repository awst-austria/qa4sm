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
from ..services.interactive_map_service import get_plot_resolution, get_cached_zarr_path
from validator.validation.globals import QR_STATUS_DICT, QR_VALUE_RANGES


# Cache TMS and transformer objects 
TMS_4326 = morecantile.tms.get("WorldCRS84Quad")  # EPSG:4326
TMS_3857 = morecantile.tms.get("WebMercatorQuad")  # EPSG:3857
TRANSFORMER_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)



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
    
    #if not bounds_data:
    if True:
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
            vmin_data, vmax_data = compute_norm_params(
                validation_id, 
                zarr_path,
                metric_name, 
                layer_name,
            )

            # Apply constraints from QR_VALUE_RANGES if they exist
            if metric_name in QR_VALUE_RANGES:
                constraints = QR_VALUE_RANGES[metric_name]

                # Use constraint if it's not None, otherwise use computed value
                vmin = constraints['vmin'] if constraints['vmin'] is not None else vmin_data
                vmax = constraints['vmax'] if constraints['vmax'] is not None else vmax_data
            else:
                # No constraints - use computed values
                vmin = vmin_data
                vmax = vmax_data

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
    cache_key = f"layer_metadata_{validation_id}"
    metadata = cache.get(cache_key)

    #if not metadata:
    if True:
        data = json.loads(request.body)
        possible_layers = data.get('possible_layers', {})

        zarr_path = get_cached_zarr_path(validation_id)
        available_layers_mapping = get_layernames(zarr_path)

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
            'status_metadata': status_metadata
        }

        cache.set(cache_key, metadata, timeout=3600)

    return JsonResponse(metadata)




    
@require_http_methods(["GET"])
def get_tile(request, validation_id, metric_name, layer_name, projection, z, x, y):

    """Serve a datashader tile with efficient DataFrame caching.
        metric_name should be metric, varname is better called layername """

    # print(f"\n{'='*80}")
    # print(f"GET_TILE CALLED: z={z}, x={x}, y={y}, projection={projection}")
    # print(f"metric={metric_name}, var={var_name}")
    # print(f"{'='*80}")

    if projection not in (4326, 3857):
        print("ERROR: Invalid projection")
        return HttpResponse("Invalid projection. Use '4326' or '3857'", status=400)

    zarr_path = get_cached_zarr_path(validation_id)
    print(f"Zarr path: {zarr_path}")

    if zarr_path is None or not os.path.exists(zarr_path):
        print("ERROR: Zarr path not found")
        return HttpResponse(status=404)

    try:
        print("Calling get_cached_dataframe_with_index...")
        df, tree, coord_cols = get_cached_dataframe_with_index(
            validation_id, layer_name, zarr_path, projection
        )

        print(f"DataFrame returned: {len(df) if df is not None else 0} rows")

        if df is None or len(df) == 0:
            print("ERROR: No data in DataFrame")
            return get_transparent_tile()

        # Select TMS based on projection
        tms = TMS_3857 if projection == 3857 else TMS_4326


        # Get tile bounds
        bbox = tms.xy_bounds(x, y, z)

        # Get spread parameters
        resolution = get_plot_resolution(validation_id)

        # Set spread and buffer based on whether data is scattered
        if resolution['is_scattered']:
            spread_px = 4
            buffer_px = 5
            marker_shape = 'circle'
        else:
            spread_px, buffer_px = get_spread_and_buffer(validation_id, z, resolution['plot_resolution'])
            marker_shape = 'square'

        print(f"Zoom {z}: spread_px={spread_px}, buffer_px={buffer_px}, points={len(df)}, scattered={resolution['is_scattered']}")

        # Calculate ranges and buffers
        x_range = bbox.right - bbox.left
        y_range = bbox.top - bbox.bottom
        x_buffer = x_range * (buffer_px / 256)
        y_buffer = y_range * (buffer_px / 256)

        # Filter data with buffered bounds
        mask = ((df[coord_cols[0]] >= bbox.left - x_buffer) & 
                (df[coord_cols[0]] <= bbox.right + x_buffer) &
                (df[coord_cols[1]] >= bbox.bottom - y_buffer) & 
                (df[coord_cols[1]] <= bbox.top + y_buffer))
        df_tile = df[mask].copy()

        if len(df_tile) == 0:
            return get_transparent_tile()

        # Map to buffered pixel space
        df_tile['px'] = ((df_tile[coord_cols[0]] - (bbox.left - x_buffer)) / 
                        (x_range + 2*x_buffer) * (256 + 2*buffer_px))
        df_tile['py'] = ((df_tile[coord_cols[1]] - (bbox.bottom - y_buffer)) / 
                        (y_range + 2*y_buffer) * (256 + 2*buffer_px))

        # Create buffered canvas
        cvs = ds.Canvas(plot_width=256 + 2*buffer_px,
                        plot_height=256 + 2*buffer_px,
                        x_range=(0, 256 + 2*buffer_px),
                        y_range=(0, 256 + 2*buffer_px))


        # Get normalization parameters and colormap
        vmin, vmax = compute_norm_params(validation_id, zarr_path, metric_name, layer_name)
        mpl_cmap = get_colormap(metric_name)

        # Check if categorical (status)
        is_categorical = metric_name == 'status' or layer_name.startswith('status')

        if is_categorical:
            # Use 'first' or 'last' reduction to preserve exact category values
            agg = cvs.points(df_tile, 'px', 'py', ds.first('value'))
            # Or use ds.last('value') if you prefer the top point to show
        else:
            agg = cvs.points(df_tile, 'px', 'py', ds.mean('value'))

        if is_categorical:
            # For categorical data, create a color key mapping
            status_codes = sorted(QR_STATUS_DICT.keys())

            # Get colors from the colormap
            colors_rgba = [mpl_cmap(i) for i in range(len(status_codes))]
            colors_hex = ['#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255)) 
                        for r, g, b, a in colors_rgba]

            # Create color_key: map each status code to its color
            color_key = {int(code): colors_hex[i] for i, code in enumerate(status_codes)}

            print(f"Status color_key: {color_key}")

            # Use categorize for discrete mapping
            img = tf.shade(agg, color_key=color_key, how='linear')
        else:
            # For continuous data, use linear mapping with span
            print(f'vmin {vmin} and vmax {vmax}')
            img = tf.shade(agg, cmap=mpl_cmap, how='linear', span=(vmin, vmax))

        # Create black halo layer
        img_halo = tf.shade(agg, cmap=['black'], how='linear')
        img_halo = tf.spread(img_halo, px=spread_px + 1, shape=marker_shape)

        # Create colored marker layer
        img = tf.spread(img, px=spread_px, shape=marker_shape)

        # Stack them (halo behind, markers on top)
        img = tf.stack(img_halo, img)


        # Crop and process
        pil_img = img.to_pil().convert('RGBA')
        pil_img = pil_img.crop((buffer_px, buffer_px, 256 + buffer_px, 256 + buffer_px))
        img_array = np.array(pil_img)

        # img_array[:, :, 3] = alpha
        pil_img = Image.fromarray(img_array, 'RGBA')

        # Save to buffer
        img_buffer = io.BytesIO()
        pil_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return HttpResponse(img_buffer.getvalue(), content_type='image/png')

    except Exception as e:
        print(f"Error generating tile: {str(e)}")
        return HttpResponse(status=500)

    except Exception as e:
        print(f"Error generating tile: {e}")
        import traceback
        traceback.print_exc()
        return get_transparent_tile()
