import numpy as np

from .. import ease
from ..elements.element import Element
from ..tween import Tween


class draw_svg(Tween):
    def __init__(self, start=[0, 0], end=[0, 1], ease=ease.linear, **kwargs):
        self.start = np.array(start)
        self.end = np.array(end)
        self.ease = ease
        super().__init__(**kwargs)

    def clamp_negative(self, x):
        if x < 0:
            return 0
        return x

    def draw_stroke(self, element, et):
        if isinstance(element, Element):
            if self.lengths.get(id(element), None):
                path_length = self.lengths[id(element)]
            else:
                path_length = element.length()
                self.lengths[element.id] = path_length
            start_ratio = (1 - et) * self.start_from + et * self.start_to
            end_ratio = (1 - et) * self.end_from + et * self.end_to
            start = start_ratio * path_length
            end = end_ratio * path_length
            element.stroke_dasharray(
                [0.00001, start, end - start,
                 self.clamp_negative(path_length - end)])
        else:
            for i in range(len(element)):
                self.draw_stroke(element[i], et)

    def update(self, t):
        et = self.ease(self.clip(t))
        self.draw_stroke(self.elements, et)
        return [self.elements]
