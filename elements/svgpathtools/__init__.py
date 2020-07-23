from .bezier import (bezier2polynomial, bezier_bounding_box,
                     bezier_by_line_intersections, bezier_intersections,
                     bezier_point, polynomial2bezier, split_bezier)
from .document import (CONVERSIONS, CONVERT_ONLY_PATHS, SVG_GROUP_TAG,
                       SVG_NAMESPACE, Document)
from .misctools import hex2rgb, rgb2hex
from .parser import parse_path
from .path import (Arc, CubicBezier, Line, Path, QuadraticBezier,
                   bezier_segment, bounding_box2path, bpoints2bezier,
                   closest_point_in_path, concatpaths, farthest_point_in_path,
                   is_bezier_path, is_bezier_segment, is_path_segment,
                   path_encloses_pt, poly2bez, polygon, polyline)
from .paths2svg import disvg, paths2Drawing, wsvg
from .polytools import imag, polyroots, polyroots01, rational_limit, real
from .smoothing import is_differentiable, kinks, smoothed_joint, smoothed_path
from .svg_io_sax import SaxDocument

try:
    from .svg_to_paths import svg2paths, svg2paths2
except ImportError:
    pass
