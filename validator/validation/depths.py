"""
Depth-layer geometry for the "Merge Layers" feature.

Pure functions over :class:`validator.models.DataVariable` objects — no database
access, no Django queries — so they can be unit tested in isolation and reused
both by the manual layer picker (where the user ticks whole layers) and by the
cross-dataset layer matching (where a target range comes from another dataset
and may cut a layer in half).

All depths are in metres below the surface.
"""

# depths come from fixtures as floats (0.07, 0.28, ...), so comparisons of
# layer boundaries need a tolerance rather than exact equality
DEPTH_TOL = 1e-9


def _bounds(variable):
    """(depth_from, depth_to) of a variable, or raise if it has no depth."""
    if variable.depth_from is None or variable.depth_to is None:
        raise ValueError(
            f"variable '{variable.short_name}' has no depth information")
    if variable.depth_to <= variable.depth_from:
        raise ValueError(
            f"variable '{variable.short_name}' has depth_to <= depth_from "
            f"({variable.depth_to} <= {variable.depth_from})")
    return variable.depth_from, variable.depth_to


def sort_by_depth(variables):
    """Variables ordered by depth, shallowest first."""
    return sorted(variables, key=lambda v: (v.depth_from, v.depth_to))


def layers_to_range(variables):
    """
    The depth range covered by a set of selected layers.

    This is the manual picking direction: the user ticks whole layers and the
    range falls out of them. Returns ``None`` for an empty selection.

    Parameters
    ----------
    variables: iterable of DataVariable
        The selected layers. Every one must carry both depth bounds.

    Returns
    -------
    (depth_from, depth_to): tuple of float, or None
    """
    variables = list(variables)
    if not variables:
        return None

    bounds = [_bounds(v) for v in variables]
    return min(b[0] for b in bounds), max(b[1] for b in bounds)


def is_contiguous(variables):
    """
    Whether the selected layers form a gap-free, non-overlapping stack.

    Non-contiguous selections are **allowed**. Picking GLDAS 0-10 plus 40-100
    and skipping 10-40 is the user's call, and the merged value stays well
    defined: the weights are the picked layers' own overlaps, so the mean
    normalises over the 0.70 m actually selected and never over the gap.

    What such a selection breaks is the *label*, not the number. Describing the
    result as "0-100 cm" would claim 30 cm that contributed nothing. Use this to
    choose how to describe a selection — a span when contiguous, the individual
    members when not — never to decide whether to permit it.
    """
    variables = list(variables)
    if len(variables) < 2:
        return True

    ordered = sort_by_depth(variables)
    for shallower, deeper in zip(ordered, ordered[1:]):
        _, upper_end = _bounds(shallower)
        lower_start, _ = _bounds(deeper)
        if abs(lower_start - upper_end) > DEPTH_TOL:
            return False
    return True


def overlap(variable, depth_from, depth_to):
    """
    How much of ``variable``'s layer lies inside [depth_from, depth_to], in metres.

    Zero when the layer is entirely outside the target. This is the quantity
    every weight is built from: a layer contributes in proportion to how much of
    the target interval it fills, which reduces to the plain layer thickness
    whenever the layer sits wholly inside the target.
    """
    layer_from, layer_to = _bounds(variable)
    return max(0.0, min(depth_to, layer_to) - max(depth_from, layer_from))


def is_extensive(variable):
    """
    Whether the stored value is a mass per unit area rather than a volumetric
    fraction, and so has to be divided by the layer thickness before layers can
    be combined. True for GLDAS (kg/m²), false for everything else so far.
    """
    from validator.validation.globals import EXTENSIVE_UNITS
    return variable.unit in EXTENSIVE_UNITS


def merge_coefficients(variables, weighted=True, target=None):
    """
    Per-column coefficients for folding several depth layers into one series.

    The merge is a plain dot product over the *raw stored* values,
    ``Σ(cᵢ · xᵢ)``, so these coefficients carry their own normalisation and any
    unit conversion. Do not hand them to :func:`numpy.average`, which would
    divide by ``Σc`` a second time.

    For an intensive (volumetric) variable the stored value already is θᵢ::

        cᵢ = wᵢ / Σw

    For an extensive one (kg/m² over the layer's full thickness Δzᵢ) recovering
    θᵢ divides by ``ρ_w · Δzᵢ``, and that fold-in is the only difference::

        cᵢ = wᵢ / (ρ_w · Δzᵢ · Σw)

    where ``wᵢ`` is the layer's overlap with the merged range when weighting is
    on, and ``1/n`` when it is off. Note the thickness division stays either
    way: an equal-weight mean of raw kg/m² values is not a soil moisture at all.

    Parameters
    ----------
    variables: iterable of DataVariable
        The layers to merge. Two or more, all carrying depth bounds.
    weighted: bool, optional (default: True)
        False gives every layer the same weight regardless of thickness.
    target: (float, float), optional
        Depth range to weight against. Defaults to the range the layers
        themselves span, which is the manual-picking case — then every overlap
        is the layer's own full thickness.

    Returns
    -------
    (columns, coefficients): (list of str, list of float)
        Column names in reader order and their coefficients, aligned.
    """
    from validator.validation.globals import WATER_DENSITY

    ordered = sort_by_depth(variables)
    if len(ordered) < 2:
        raise ValueError('merging needs at least two layers, got '
                         f'{len(ordered)}')

    if target is None:
        target = layers_to_range(ordered)

    if weighted:
        weights = [overlap(v, *target) for v in ordered]
    else:
        weights = [1.0 / len(ordered)] * len(ordered)

    total = sum(weights)
    if total <= 0:
        raise ValueError('selected layers do not overlap the target range '
                         f'{target}')

    coefficients = []
    for variable, weight in zip(ordered, weights):
        coefficient = weight / total
        if is_extensive(variable):
            coefficient /= WATER_DENSITY * variable.thickness
        coefficients.append(coefficient)

    return [v.short_name for v in ordered], coefficients


def depth_label(variables):
    """
    Human-readable depth description, in centimetres.

    Contiguous picks get a single span (``"0-40 cm"``). Gapped picks are legal
    but a span would overclaim the missing layers, so
    they are described by their members instead (``"0-10, 40-100 cm"``).
    """
    ordered = sort_by_depth(variables)
    if is_contiguous(ordered):
        depth_from, depth_to = layers_to_range(ordered)
        return '%g-%g cm' % (depth_from * 100, depth_to * 100)

    spans = ['%g-%g' % (v.depth_from * 100, v.depth_to * 100) for v in ordered]
    return '%s cm' % ', '.join(spans)


def depth_file_label(variables):
    """
    Filesystem-safe depth description, for naming result files.

    ``"0-40cm_merged"``, or ``"0-10_40-100cm_merged"`` when the picked layers
    are not adjacent. No spaces, commas or brackets, so it survives being
    joined into a file name and read back off disk.
    """
    return depth_label(variables).replace(', ', '_').replace(' ', '') + '_merged'


def merged_labels(variables):
    """
    The two name strings a merged series is written out with.

    Returns ``(pretty, short)`` for the ``val_dc_variable`` and
    ``val_dc_variable_pretty_name`` netCDF attributes respectively.
    This returns pretty and short names in
    attribute order, so pass them straight through.
    """
    ordered = sort_by_depth(variables)
    return ('%s (merged)' % depth_label(ordered),
            '+'.join(v.short_name for v in ordered))


def merged_unit(variables, current_unit):
    """
    The unit a merged series carries. Extensive inputs come out volumetric,
    because :func:`merge_coefficients` folds the mass-to-θ conversion in;
    everything else keeps the unit it already had.
    """
    from validator.validation.globals import VOLUMETRIC_UNIT
    if any(is_extensive(v) for v in variables):
        return VOLUMETRIC_UNIT
    return current_unit


def range_to_layers(depth_from, depth_to, variables):
    """
    The layers of a dataset that contribute to a target depth range.

    This is the matching direction, and the mirror image of
    :func:`layers_to_range`. It is unused by the manual picker — where the
    target is by construction the union of the ticked layers, so every overlap
    equals the full layer thickness — and becomes the engine of cross-dataset
    layer matching, where a target taken from one dataset can cut a layer of
    another in half.

    Only variables marked as disjoint layers take part; aggregates such as
    ``rzsm_1m`` (which spans 0-1 m and would double-count the layers it
    subsumes) and variables without depths are skipped.

    Parameters
    ----------
    depth_from, depth_to: float
        The target range, in metres.
    variables: iterable of DataVariable
        Candidate variables, e.g. ``version.variables.all()``.

    Returns
    -------
    list of (DataVariable, overlap_in_metres), shallowest first, excluding
    layers that do not overlap the target at all.
    """
    if depth_to <= depth_from:
        raise ValueError(
            f"depth_to must be greater than depth_from "
            f"({depth_to} <= {depth_from})")

    layers = [v for v in variables if v.is_mergeable_layer]

    contributing = []
    for layer in sort_by_depth(layers):
        ov = overlap(layer, depth_from, depth_to)
        if ov > DEPTH_TOL:
            contributing.append((layer, ov))

    return contributing
