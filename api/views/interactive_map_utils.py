# UTILS AND COLORMAP

from django.http import JsonResponse, HttpResponse
from PIL import Image
from django.core.cache import cache
import io
import re
import matplotlib.cm as cm
import xarray as xr
import numpy as np
from ..services.interactive_map_service import get_plot_resolution
from functools import lru_cache
from django.core.cache import cache
from pyproj import Transformer
from validator.validation.globals import QR_COLORMAPS, QR_STATUS_DICT, QR_VALUE_RANGES, QR_CCI_LANDCOVER, QR_KG_CLIMATE, QR_METRICS_DESCRIPTION

# Define transformer at module level
TRANSFORMER_TO_4326 = Transformer.from_crs("EPSG:3857",
                                           "EPSG:4326",
                                           always_xy=True)
TRANSFORMER_TO_3857 = Transformer.from_crs("EPSG:4326",
                                           "EPSG:3857",
                                           always_xy=True)


@lru_cache(maxsize=10)
def get_cached_zarr_dataset(zarr_path):
    """
    Load and cache the zarr dataset directly.
    """
    return xr.open_zarr(zarr_path)


def get_cache_key(validation_id, var_name):
    """Generate consistent cache keys"""
    return f"validation_{validation_id}_{var_name}"


def compute_norm_params(validation_id, zarr_path, metric_name, layer_name):
    """Compute normalization parameters for a specific variable, respecting constraints"""
    cache_key = get_cache_key(validation_id, layer_name)
    cached_params = cache.get(cache_key)

    if cached_params:
        return cached_params

    try:
        # Special handling for status (categorical)
        if metric_name and (metric_name == 'status'
                            or layer_name.startswith('status')):
            # Status uses fixed range based on status codes
            vmin = min(QR_STATUS_DICT.keys())
            vmax = max(QR_STATUS_DICT.keys())
            cache.set(cache_key, (vmin, vmax), 86400)
            return vmin, vmax

        # For continuous data, compute from actual data
        ds = get_cached_zarr_dataset(zarr_path)

        # Select tsw='bulk' if needed
        if 'tsw' in ds.dims:
            ds = ds.sel(tsw='bulk')

        var_data = ds[layer_name].values
        vmin_data = float(np.nanmin(var_data))
        vmax_data = float(np.nanmax(var_data))

        vmax = max(abs(vmin_data), abs(vmax_data))
        vmin = -abs(vmax)

        # Apply constraints from QR_VALUE_RANGES if they exist
        if metric_name and metric_name in QR_VALUE_RANGES:
            constraints = QR_VALUE_RANGES[metric_name]
            # Use constraint if it's not None, otherwise use computed value
            vmin = constraints['vmin'] if constraints[
                'vmin'] is not None else vmin
            vmax = constraints['vmax'] if constraints[
                'vmax'] is not None else vmax

        # Cache for 24 hours
        cache.set(cache_key, (vmin, vmax), 86400)
        return vmin, vmax

    except Exception as e:
        print(f"Error computing normalization parameters: {e}")
        return 0.0, 1.0


def get_transparent_tile():
    """Get cached transparent tile bytes"""
    cache_key = 'transparent_tile_png'
    tile_bytes = cache.get(cache_key)

    if not tile_bytes:
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        tile_bytes = img_buffer.getvalue()
        cache.set(cache_key, tile_bytes, timeout=None)  # Cache forever

    return HttpResponse(tile_bytes, content_type='image/png')


def get_colormap(metric_name):
    """Get cached colormap for a specific metric"""
    cache_key = f"colormap_{metric_name}"
    cached_colormap = cache.get(cache_key)

    if cached_colormap:
        return cached_colormap

    try:
        # Get the matplotlib colormap from QR_COLORMAPS
        if metric_name in QR_COLORMAPS:
            mpl_colormap = QR_COLORMAPS[metric_name]
        else:
            # Fallback to a default colormap if metric not found
            mpl_colormap = cm.get_cmap(
                'viridis')

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

def clip_trailing_int(name: str) -> str:
    """Remove trailing dataset identifier from triple collocation metrics.

    Example: 'err_std_0-ISMN' -> 'err_std'
    """
    return re.sub(r'_\d+(?:-.*)?$', '', name)


def get_metrics_description(metric_name: str, unit: dict | None) -> str | None:
    """Look up metric description and format with unit if available."""
    if not unit:
        return None

    common_unit = unit.get('common_unit')
    if not common_unit:
        return None

    candidates = (metric_name, clip_trailing_int(metric_name))

    for key in candidates:
        if key and (template := QR_METRICS_DESCRIPTION.get(key)):
            return template.format(common_unit)

    print(f"Unknown metric_name: {metric_name!r} (also tried {candidates[1]!r})")
    return None


def get_colormap_metadata(metric_name: str, unit: dict | None = None) -> dict:
    """Get static colormap metadata (gradient, type, categories) - NO file I/O.

    Args:
        metric_name: Name of metric for colorbar (e.g. 'n_obs', 'status', 'BIAS')
        unit: Dict with 'common_unit' and optionally 'from_scaling_ref', or None

    Returns:
        Dict with keys: gradient, is_categorical, colormap_info, metrics_description,
        and optionally 'categories' for status metrics.
    """
    cache_key = f"colormap_metadata_{metric_name}"

    # if cached := cache.get(cache_key):
    #     return cached

    colormap = get_colormap(metric_name)

    result = {
        'gradient': generate_css_gradient(colormap, metric_name),
        'is_categorical': metric_name == 'status',
        'colormap_info': get_colormap_type(colormap),
        'metrics_description': get_metrics_description(metric_name, unit),
    }

    if metric_name == 'status':
        result['categories'] = QR_STATUS_DICT

    cache.set(cache_key, result, None)
    return result



def get_layernames(zarr_path):
    """Get information about all variables in the Zarr dataset"""
    cache_key = f"dataset_info_{zarr_path}"
    cached_info = cache.get(cache_key)

    if cached_info:
        return cached_info

    try:
        ds = get_cached_zarr_dataset(zarr_path)

        excluded = {'tsw', 'lon', 'lat', 'idx', 'gpi'}
        descriptions = {}

        for var_name in ds.data_vars:
            if var_name not in excluded:
                descriptions[var_name] = ds[var_name].attrs.get(
                    'long_name', var_name)

        # Cache for 1 hour
        cache.set(cache_key, descriptions, 3600)
        return descriptions

    except Exception as e:
        print(f"Error reading zarr dataset info: {e}")
        return {}


def get_actual_status_values(zarr_path, var_name):
    """Get unique status values that actually occur in the data"""
    try:
        ds = get_cached_zarr_dataset(zarr_path)
        if var_name in ds.data_vars:
            data = ds[var_name].values
            # Get unique values, excluding NaN
            unique_vals = np.unique(data[~np.isnan(data)])
            return sorted([int(v) for v in unique_vals])
        return []
    except Exception as e:
        print(f"Error reading status values: {e}")
        return []


def build_status_legend_data(colormap_info, zarr_path=None, var_name=None):
    """Build legend entries from colormap info and status categories, filtered by actual values"""
    import numpy as np

    if not colormap_info.get(
            'is_categorical') or 'categories' not in colormap_info:
        return None

    categories = colormap_info['categories']
    colors = colormap_info['colormap_info'].get('colors', [])

    # Convert colors to list if it's a numpy array
    if isinstance(colors, np.ndarray):
        colors = colors.tolist()

    # Get actual status values if zarr_path provided
    if zarr_path and var_name:
        actual_values = get_actual_status_values(zarr_path, var_name)
    else:
        # Show all categories if we can't check
        actual_values = list(categories.keys())

    # Build legend entries only for occurring values
    entries = []
    sorted_categories = sorted(categories.items(), key=lambda x: int(x[0]))

    for status_code, label in sorted_categories:
        status_code_int = int(status_code)

        # Only include if this status actually occurs in the data
        if status_code_int not in actual_values:
            continue

        # Map status code to color index (shift by 1)
        color_index = status_code_int + 1

        # Get color from colormap
        if color_index < len(colors):
            rgba = colors[color_index]
            # Ensure rgba is also a list (in case colors wasn't converted above)
            if isinstance(rgba, np.ndarray):
                rgba = rgba.tolist()

            color = f"rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3] if len(rgba) > 3 else 1.0})"
        else:
            color = '#cccccc'

        entries.append({
            'value': status_code_int,
            'label': label,
            'color': color
        })

    return {'entries': entries}


def calculate_spread(zoom_level, plot_resolution):
    """
    Calculate spread pixels based on zoom level and plot resolution.

    Args:
        zoom_level: zoom level (2-14)
        plot_resolution: desired plot resolution in degrees (0.005-0.4)

    Returns:
        int: number of pixels to spread
    """
    if not plot_resolution:
        plot_resolution = 0.25

    if plot_resolution <= 0.1:
        # Fine resolution: exponential formula
        multiplier = 450
        exponent = 3.6
        divisor = 1840
        return max(
            int((plot_resolution * multiplier + 10) * zoom_level**exponent /
                divisor), 1)

    # Coarse resolution (plot_resolution > 0.1)
    # Scale all values by plot_resolution/0.35 to handle different resolutions
    scale = plot_resolution / 0.35

    if zoom_level <= 4.5:
        # Very low zoom: minimal spread to avoid artifacts
        return max(int(zoom_level * scale), 2)

    elif zoom_level <= 9:
        # Mid-low zoom: gradual ramp toward transition
        base_spread = int(7 * (zoom_level - 5)**1.6 + 6)
        return int(base_spread * scale)

    else:
        # zoom >= 10: full rectangle mode with gradual quadratic ramp
        base_spread = int(133 + 67 * (zoom_level - 10) + 33 *
                          (zoom_level - 10)**2)
        return int(base_spread * scale)


def get_spread_and_buffer(validation_id, zoom_level, plot_resolution):
    resolution_key = plot_resolution if plot_resolution is not None else 'none'
    cache_key = f'spread_buffer:{validation_id}:{zoom_level}:{resolution_key}'

    result = cache.get(cache_key)

    if result is None:
        print(f"CACHE MISS: {cache_key}")  # Add logging
        spread_px = calculate_spread(zoom_level, plot_resolution)
        buffer_px = spread_px + 1
        result = (spread_px, buffer_px)
        cache.set(cache_key, result, 3600)
    else:
        print(f"CACHE HIT: {cache_key}")  # Add logging

    return result


# 1. In-memory LRU cache for DataFrames (most recent validations)
@lru_cache(
    maxsize=10)  # Keep last 10 validation_id + var_name combos in memory
def get_cached_dataframe(validation_id, var_name, zarr_path):
    """
    Load and cache DataFrame in memory.
    Cache key is based on validation_id and var_name.
    """
    ds_zarr = get_cached_zarr_dataset(zarr_path)

    if var_name not in ds_zarr.data_vars:
        return None

    da = ds_zarr[var_name]
    df = da.to_dataframe(name='value').reset_index()
    df = df.dropna(subset=['value'])
    return df


# 2. Spatial indexing for faster filtering
def create_spatial_index(df, coord_cols=('lon', 'lat')):
    """
    Create a simple spatial index using binning.
    This helps quickly filter points for a given tile.
    """
    from scipy.spatial import cKDTree

    # Create KD-tree for spatial queries
    coords = df[list(coord_cols)].values
    tree = cKDTree(coords)

    return tree, coords


@lru_cache(maxsize=10)
def get_cached_dataframe_with_index(validation_id,
                                    layer_name,
                                    zarr_path,
                                    projection,
                                    is_scattered=False):
    """
    Load DataFrame and create spatial index.
    """
    ds_zarr = get_cached_zarr_dataset(zarr_path)

    if layer_name not in ds_zarr.data_vars:
        return None, None, None

    da = ds_zarr[layer_name]
    df = da.to_dataframe(name='value').reset_index()
    df = df.dropna(subset=['value'])

    # Transform if needed
    if projection == 3857:
        df = df.copy()
        df['x'], df['y'] = TRANSFORMER_TO_3857.transform(
            df['lon'].values, df['lat'].values)
        coord_cols = ('x', 'y')
    else:
        coord_cols = ('lon', 'lat')

    # Create spatial index
    tree, coords = create_spatial_index(df, coord_cols)

    print(
        f"Loaded DataFrame with spatial index for {validation_id}/{layer_name}: {len(df)} points"
    )

    return df, tree, coord_cols


def get_point_value(request, validation_id, layer_name, zarr_path, x, y, z,
                    projection):
    """
    Get value at point using direct xarray operations.
    Returns all candidates within threshold, with disambiguation info.
    """
    # Transform coordinates to EPSG:4326 if needed
    if projection == 3857:
        query_lon, query_lat = TRANSFORMER_TO_4326.transform(x, y)
    elif projection == 4326:
        query_lon, query_lat = x, y
    else:
        return JsonResponse({'error': f'Unsupported projection: {projection}'},
                            status=400)

    # Get resolution/distance threshold
    resolution = get_plot_resolution(validation_id)

    if not resolution['is_scattered']:
        max_distance_deg = resolution['plot_resolution'] * (2 / z)**0.25
    else:
        max_distance_deg = 4 / (z**1.75)

    try:
        ds = get_cached_zarr_dataset(zarr_path)

        if layer_name not in ds.data_vars:
            return JsonResponse({'error': f'Variable {layer_name} not found'},
                                status=404)

        lons = ds['lon'].values
        lats = ds['lat'].values

        # Simple distance calculation in degrees
        distances = np.sqrt((lons - query_lon)**2 + (lats - query_lat)**2)

        # Find ALL points within threshold
        within_threshold_mask = distances <= max_distance_deg
        candidate_indices = np.where(within_threshold_mask)[0]

        if len(candidate_indices) == 0:
            return JsonResponse({'error': 'No data found at this location'},
                                status=404)

        # Sort candidates by distance (nearest first)
        candidate_distances = distances[candidate_indices]
        sorted_order = np.argsort(candidate_distances)
        candidate_indices = candidate_indices[sorted_order]

        # Build candidate list
        candidates = []
        is_ismn = resolution['is_ismn']

        for idx in candidate_indices:
            idx = int(idx)

            # Extract value and skip NaN
            raw_value = float(ds[layer_name].isel(loc=idx).values)
            if np.isnan(raw_value):
                continue

            response_value = round(raw_value, 3)
            if layer_name.startswith('status'):
                response_value = QR_STATUS_DICT[int(raw_value)]

            candidate = {
                'gpi': idx,
                'value': str(response_value),
                'lat': float(lats[idx]),
                'lon': float(lons[idx]),
                'distance': float(distances[idx])
            }

            if is_ismn:
                _add_ismn_metadata(ds, idx, candidate)

            candidates.append(candidate)

        # No valid candidates after NaN filtering
        if len(candidates) == 0:
            return JsonResponse({'error': 'No valid data at this location'},
                                status=404)

        return JsonResponse({
            'candidates': candidates,
            'multiple_found': len(candidates) > 1,
            'source': 'ismn' if is_ismn else 'gridded',
            'is_ismn': is_ismn
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _add_ismn_metadata(ds, idx, candidate):
    """Helper to add ISMN metadata to a candidate."""
    metadata_vars = [
        'station', 'network', 'lc_2010', 'climate_KG', 'frm_class',
        'instrument', 'instrument_depthfrom', 'instrument_depthto'
    ]

    for meta_var in metadata_vars:
        if meta_var not in ds.data_vars and meta_var not in ds.coords:
            continue

        val = ds[meta_var].isel(loc=idx).values
        if hasattr(val, 'item'):
            val = val.item()
        elif isinstance(val, (bytes, np.bytes_)):
            val = val.decode('utf-8')
        else:
            val = str(val)

        if meta_var == 'lc_2010':
            lc_code = int(val)
            lc_value = QR_CCI_LANDCOVER.get(lc_code, "Unknown")
            candidate[meta_var] = f"{lc_value} ({lc_code})"
        elif meta_var == 'climate_KG':
            kg_value = QR_KG_CLIMATE.get(val, "Unknown")
            candidate[meta_var] = f"{kg_value} ({val})"
        else:
            candidate[meta_var] = val
