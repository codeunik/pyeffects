import math
from copy import deepcopy

from . import ease
from ..elements.path import Path
from .tween import Tween


class motion_path(Tween):
    def __init__(self,
                 path,
                 start=0.0,
                 end=1.0,
                 element_anchor=[0.5, 0.5, 0.5],
                 auto_rotate=True,
                 ease=ease.smooth,
                 **kwargs):

        self.path = path
        self.start = start
        self.end = end
        self.element_anchor = element_anchor
        self.auto_rotate = auto_rotate
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        t = 1 if t > 1 else t
        et = self.ease(t)
        et = self.clip((1 - et) * self.start + et * self.end)
        position = self.path._data_2d.point(et)
        bbox = self.elements.bbox()
        z_coord = (bbox[0][2] + bbox[1][2]) / 2
        self.elements.place_at_pos(position.real, position.imag, z_coord,
                                   *self.element_anchor)
        if self.auto_rotate:
            unit_tangent = self.path.unit_tangent(et)
            self.elements.dynamic_rotate(
                math.degrees(math.atan2(unit_tangent.imag, unit_tangent.real)),
                [0, 0, 1], *self.element_anchor)
        return [self.elements]
