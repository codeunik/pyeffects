from copy import deepcopy
import colorsys
import numpy as np

# from .defs import LinearGradient, RadialGradient
from .place import Place
from .transform import Transform
from .utils import Color


class Element(Transform, Place):
    attrs = [
        "_stroke", "_stroke_width", "_fill", "_opacity", "_fill_opacity", "_stroke_opacity",
        "_stroke_linecap", "_stroke_linejoin", "_stroke_dasharray", "_fill_rule",
        "_stroke_miterlimit", "_stroke_dashoffset", "_clip_path", "_mask", "_filter"
    ]

    def __init__(self):

        self._stroke = "nil"
        self._stroke_width = "nil"
        self._fill = "nil"
        self._opacity = 1
        self._fill_opacity = "nil"
        self._stroke_opacity = "nil"
        self._stroke_linecap = "round"
        self._stroke_linejoin = "round"
        self._stroke_miterlimit = "nil"
        self._stroke_dashoffset = "nil"
        self._stroke_dasharray = "nil"    # list
        self._fill_rule = "nil"
        self._clip_path = "nil"
        self._mask = "nil"
        self._filter = "nil"
        self._z_index = None
        self.additional_data = dict()

        Transform.__init__(self)

    def _draw(self):
        attr_str = ""
        for attr in Element.attrs:
            if getattr(self, attr) is not "nil":
                attr_str += getattr(self, f"_str{attr}")() + " "

        return attr_str

    def copy(self):
        return deepcopy(self)

    def z_index(self, z_index):
        self._z_index = z_index
        return self

    def stroke(self, color):
        # if isinstance(color, LinearGradient):
        #     self._stroke = color
        # elif isinstance(color, RadialGradient):
        #     self._stroke = color
        # else:
        self._stroke = color
        return self

    def fill(self, color):
        # if isinstance(color, LinearGradient):
        #     self._fill = color
        # elif isinstance(color, RadialGradient):
        #     self._fill = color
        # else:
        self._fill = color
        return self

    def stroke_width(self, stroke_width):
        self._stroke_width = stroke_width
        return self

    def opacity(self, opacity):
        self._opacity = opacity
        return self

    def fill_opacity(self, fill_opacity):
        self._fill_opacity = fill_opacity
        return self

    def stroke_opacity(self, stroke_opacity):
        self._stroke_opacity = stroke_opacity
        return self

    def stroke_linecap(self, stroke_linecap):
        self._stroke_linecap = stroke_linecap
        return self

    def stroke_linejoin(self, stroke_linejoin):
        self._stroke_linejoin = stroke_linejoin
        return self

    def stroke_dasharray(self, stroke_dasharray):
        self._stroke_dasharray = np.array(stroke_dasharray)
        return self

    def fill_rule(self, fill_rule):
        self._fill_rule = fill_rule
        return self

    def stroke_miterlimit(self, stroke_miterlimit):
        self._stroke_miterlimit = stroke_miterlimit
        return self

    def stroke_dashoffset(self, stroke_dashoffset):
        self._stroke_dashoffset = stroke_dashoffset
        return self

    def clip_path(self, clip_path):
        self._clip_path = clip_path
        return self

    def mask(self, mask):
        self._mask = mask
        return self

    def filter(self, filter):
        self._filter = filter
        return self

    def get_z_index(self):
        return 0 if self._z_index is None else self._z_index

    def get_stroke(self):
        return self._stroke

    def get_fill(self):
        return self._fill

    def get_stroke_width(self):
        return self._stroke_width

    def get_opacity(self):
        return self._opacity

    def get_fill_opacity(self):
        return self._fill_opacity

    def get_stroke_opacity(self):
        return self._stroke_opacity

    def get_stroke_linecap(self):
        return self._stroke_linecap

    def get_stroke_linejoin(self):
        return self._stroke_linejoin

    def get_stroke_dasharray(self):
        return self._stroke_dasharray

    def get_fill_rule(self):
        return self._fill_rule

    def get_stroke_miterlimit(self):
        return self._stroke_miterlimit

    def get_stroke_dashoffset(self):
        return self._stroke_dashoffset

    def get_clip_path(self):
        return self._clip_path

    def get_mask(self):
        return self._mask

    def get_filter(self):
        return self._filter

    def _str_color(self, color):
        if type(color) == str:
            return color
        elif color.specification == 'hsv':
            return f"rgb{tuple((np.array(colorsys.hsv_to_rgb(*color.value))*255).astype(int))}"
        elif color.specification == 'rgb':
            return f"rgb{tuple((color.value*255).astype(int))}"

    def _str_stroke(self):
        # if isinstance(self._stroke, LinearGradient):
        #     return f'stroke="url(#{self._stroke.id})"'
        # elif isinstance(self._stroke, RadialGradient):
        #     return f'stroke="url(#{self._stroke.id})"'
        return f'stroke="{self._str_color(self._stroke)}"'

    def _str_fill(self):
        # if isinstance(self._fill, LinearGradient):
        #     return f'fill="url(#{self._fill.id})"'
        # elif isinstance(self._fill, RadialGradient):
        #     return f'fill="url(#{self._fill.id})"'
        return f'fill="{self._str_color(self._fill)}"'

    def _str_stroke_width(self):
        return f'stroke-width="{self._stroke_width}"'

    def _str_opacity(self):
        return f'opacity="{self._opacity}"'

    def _str_fill_opacity(self):
        return f'fill-opacity="{self._fill_opacity}"'

    def _str_stroke_opacity(self):
        return f'stroke-opacity="{self._stroke_opacity}"'

    def _str_stroke_linecap(self):
        return f'stroke-linecap="{self._stroke_linecap}"'

    def _str_stroke_linejoin(self):
        return f'stroke-linejoin="{self._stroke_linejoin}"'

    def _str_stroke_dasharray(self):
        border_len = self.border_length()
        stroke_dasharray = self._stroke_dasharray * border_len
        return f'stroke-dasharray=\"{" ".join(str(x) for x in stroke_dasharray)}\"'

    def _str_fill_rule(self):
        return f'fill-rule="{self._fill_rule}"'

    def _str_stroke_miterlimit(self):
        return f'stroke-miterlimit="{self._stroke_miterlimit}"'

    def _str_stroke_dashoffset(self):
        border_len = self.border_length()
        return f'stroke-dashoffset="{self._stroke_dashoffset * border_len}"'

    def _str_clip_path(self):
        return f'clip-path="url(#{self._clip_path.id})"'

    def _str_mask(self):
        return f'mask="url(#{self._mask.id})"'

    def _str_filter(self):
        return f'filter="url(#{self._filter.id})"'

