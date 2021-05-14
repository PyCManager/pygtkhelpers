# https://github.com/sci-bots/svg-model/blob/master/svg_model/__init__.py#L14
import six
import re
import pint  # Unit conversion from inches to mm
import logging
import pandas as pd

from six.moves import map
from six.moves import cStringIO as StringIO

XHTML_NAMESPACE = "http://www.w3.org/2000/svg"
NSMAP = {'svg': XHTML_NAMESPACE}
INKSCAPE_NSMAP = NSMAP.copy()
INKSCAPE_NSMAP['inkscape'] = 'http://www.inkscape.org/namespaces/inkscape'

ureg = pint.UnitRegistry()

INKSCAPE_PPI = 90
INKSCAPE_PPmm = INKSCAPE_PPI / (1 * ureg.inch).to('mm')

float_pattern = r'[+-]?\d+(\.\d+)?([eE][+-]?\d+)?'  # 2, 1.23, 23e39, 1.23e-6, etc.
cre_path_command = re.compile(r'((?P<xy_command>[ML])\s+(?P<x>{0}),\s*(?P<y>{0})\s*|'
                              r'(?P<x_command>[H])\s+(?P<hx>{0})\s*|'
                              r'(?P<y_command>[V])\s+(?P<vy>{0})\s*|'
                              r'(?P<command>[Z]\s*))'
                              .format(float_pattern))

logger = logging.getLogger(__name__)


def shape_path_points(svg_path_d):
    """
    Parameters
    ----------
    svg_path_d : str
        ``"d"`` attribute of SVG ``path`` element.
    Returns
    -------
    list
        List of coordinates of points found in SVG path.
        Each point is represented by a dictionary with keys ``x`` and ``y``.
    """
    # TODO Add support for relative commands, e.g., `l, h, v`.
    def _update_path_state(path_state, match):
        if match.group('xy_command'):
            for dim_j in 'xy':
                path_state[dim_j] = float(match.group(dim_j))
            if path_state.get('x0') is None:
                for dim_j in 'xy':
                    path_state['%s0' % dim_j] = path_state[dim_j]
        elif match.group('x_command'):
            path_state['x'] = float(match.group('hx'))
        elif match.group('y_command'):
            path_state['y'] = float(match.group('vy'))
        elif match.group('command') == 'Z':
            for dim_j in 'xy':
                path_state[dim_j] = path_state['%s0' % dim_j]
        return path_state

    # Some commands in a SVG path element `"d"` attribute require previous state.
    #
    # For example, the `"H"` command is a horizontal move, so the previous
    # ``y`` position is required to resolve the new `(x, y)` position.
    #
    # Iterate through the commands in the `"d"` attribute in order and maintain
    # the current path position in the `path_state` dictionary.
    path_state = {'x': None, 'y': None}
    return [{k: v for k, v in six.iteritems(_update_path_state(path_state, match_i)) if k in 'xy'} for match_i in cre_path_command
        .finditer(svg_path_d)]


def scale_to_fit_a_in_b(a_shape, b_shape):
    """
    Return scale factor (scalar float) to fit `a_shape` into `b_shape` while
    maintaining aspect ratio.
    Arguments
    ---------
    a_shape, b_shape : pandas.Series
        Input shapes containing numeric `width` and `height` values.
    Returns
    -------
    float
        Scale factor to fit :data:`a_shape` into :data:`b_shape` while
        maintaining aspect ratio.
    """
    # Normalize the shapes to allow comparison.
    a_shape_normal = a_shape / a_shape.max()
    b_shape_normal = b_shape / b_shape.max()

    if a_shape_normal.width > b_shape_normal.width:
        a_shape_normal *= b_shape_normal.width / a_shape_normal.width

    if a_shape_normal.height > b_shape_normal.height:
        a_shape_normal *= b_shape_normal.height / a_shape_normal.height

    return a_shape_normal.max() * b_shape.max() / a_shape.max()


def svg_shapes_to_df(
        svg_source,
        xpath='//svg:path | //svg:polygon',
        namespaces=INKSCAPE_NSMAP
):
    """
    Construct a data frame with one row per vertex for all shapes in
    :data:`svg_source``.
    Arguments
    ---------
    svg_source : str or file-like
        A file path, URI, or file-like object.
    xpath : str, optional
        XPath path expression to select shape nodes.
        By default, all ``svg:path`` and ``svg:polygon`` elements are selected.
    namespaces : dict, optional
        Key/value mapping of XML namespaces.
    Returns
    -------
    pandas.DataFrame
        Frame with one row per vertex for all shapes in :data:`svg_source`,
        with the following columns:
         - ``vertex_i``: The index of the vertex within the corresponding
           shape.
         - ``x``: The x-coordinate of the vertex.
         - ``y``: The y-coordinate of the vertex.
         - other: attributes of the SVG shape element (e.g., ``id``, ``fill``,
            etc.)
    """
    from lxml import etree

    e_root = etree.parse(svg_source)
    frames = []
    attribs_set = set()

    # Get list of attributes that are set in any of the shapes (not including
    # the `svg:path` `"d"` attribute or the `svg:polygon` `"points"`
    # attribute).
    #
    # This, for example, collects attributes such as:
    #
    #  - `fill`, `stroke` (as part of `"style"` attribute)
    #  - `"transform"`: matrix, scale, etc.
    for shape_i in e_root.xpath(xpath, namespaces=namespaces):
        attribs_set.update(list(shape_i.attrib.keys()))

    for k in ('d', 'points'):
        if k in attribs_set:
            attribs_set.remove(k)

    attribs = list(sorted(attribs_set))

    # Always add 'id' attribute as first attribute.
    if 'id' in attribs:
        attribs.remove('id')
    attribs.insert(0, 'id')

    for shape_i in e_root.xpath(xpath, namespaces=namespaces):
        # Gather shape attributes from SVG element.
        base_fields = [shape_i.attrib.get(k, None) for k in attribs]

        if shape_i.tag == '{http://www.w3.org/2000/svg}path':
            # Decode `svg:path` vertices from [`"d"`][1] attribute.
            #
            # [1]: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
            points_i = [base_fields + [i] + [point_i.get(k) for k in 'xy']
                        for i, point_i in
                        enumerate(shape_path_points(shape_i.attrib['d']))]
        elif shape_i.tag == '{http://www.w3.org/2000/svg}polygon':
            # Decode `svg:polygon` vertices from [`"points"`][2] attribute.
            #
            # [2]: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/points
            points_i = [base_fields + [i] + list(map(float, v.split(',')))
                        for i, v in enumerate(shape_i.attrib['points']
                                              .strip().split(' '))]
        else:
            logger.warning('Unsupported shape tag type: %s' % shape_i.tag)
            continue
        frames.extend(points_i)
    if not frames:
        # There were no shapes found, so set `frames` list to `None` to allow
        # an empty data frame to be created.
        frames = None
    return pd.DataFrame(frames, columns=attribs + ['vertex_i', 'x', 'y'])


def svg_polygons_to_df(
        svg_source,
        xpath='//svg:polygon',
        namespaces=INKSCAPE_NSMAP
):
    """
    Construct a data frame with one row per vertex for all shapes (e.g.,
    ``svg:path``, ``svg:polygon``) in :data:`svg_source``.
    Arguments
    ---------
    svg_source : str or file-like
        A file path, URI, or file-like object.
    xpath : str, optional
        XPath path expression to select shape nodes.
    namespaces : dict, optional
        Key/value mapping of XML namespaces.
    Returns
    -------
    pandas.DataFrame
        Frame with one row per vertex for all shapes in :data:`svg_source`,
        with the following columns:
         - ``path_id``: The ``id`` attribute of the corresponding shape.
         - ``vertex_i``: The index of the vertex within the corresponding
           shape.
         - ``x``: The x-coordinate of the vertex.
         - ``y``: The y-coordinate of the vertex.
    .. note:: Deprecated in :mod:`svg_model` 0.5.post10
        :func:`svg_polygons_to_df` will be removed in :mod:`svg_model` 1.0, it
        is replaced by :func:`svg_shapes_to_df` because the latter is more
        general and works with ``svg:path`` and ``svg:polygon`` elements.
    """
    logger.warning("The `svg_polygons_to_df` function is deprecated.  Use `svg_shapes_to_df` instead.")
    result = svg_shapes_to_df(svg_source, xpath=xpath, namespaces=namespaces)
    return result[['id', 'vertex_i', 'x', 'y']].rename(columns={'id': 'path_id'})
