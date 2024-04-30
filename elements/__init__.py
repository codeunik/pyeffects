from .camera import Camera
from .defs import ClipPath, LinearGradient, Mask, RadialGradient, FilterEffect, Gourad
from .frame import Frame
from .group import Group
from .image import Image, Video
from .latex import Tex, TexConfig
from .light import Light
#from .mesh import Face, Mesh, parse_obj_file
from .path import Path
from .shapes import *
from .svg_parser import SVGParser
from .utils import *

from .text import Text
from .textbox import TextBox

from .element import Element

# to escape circular import
def _str_stroke(self):
    if isinstance(self._stroke, LinearGradient):
        return f'stroke="url(#{self._stroke.id})"'
    elif isinstance(self._stroke, RadialGradient):
        return f'stroke="url(#{self._stroke.id})"'
    return f'stroke="{self._str_color(self._stroke)}"'

def _str_fill(self):
    if isinstance(self._fill, LinearGradient):
        return f'fill="url(#{self._fill.id})"'
    elif isinstance(self._fill, RadialGradient):
        return f'fill="url(#{self._fill.id})"'
    return f'fill="{self._str_color(self._fill)}"'

Element._str_stroke = _str_stroke
Element._str_fill = _str_fill