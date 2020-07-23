import numpy as np

from . import ease
from .elements.element import Element
from .elements.group import Group


class Tween:
    def __init__(self, on_update=None, on_update_args=None):

        self.on_update = on_update
        self.on_update_args = on_update_args

        self.start_frame = 0
        self.end_frame = -1
        self.motion_duration = -1

    def set_elements(self, elements):
        self.elements = elements

    def set_ease(self, ease):
        self.ease = ease

    def parse_elements(self):
        return self.elements

    def exec(self, frame_number):
        t = self.progress(frame_number)
        if self.on_update:
            self.on_update(*self.on_update_kwargs, t=t)

        return self.update(t)

    def update(self, t):
        pass

    def progress(self, frame_number):
        if frame_number < self.start_frame:
            return -1
        elif frame_number > self.end_frame:
            return 2
        elif frame_number == self.start_frame:
            return 0
        elif frame_number == self.end_frame:
            return 1
        else:
            return (frame_number - self.start_frame) / self.motion_duration

    def timing(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.motion_duration = end_frame - start_frame

    def clip(self, t):
        if 0 <= t <= 1:
            return t
        elif t < 0:
            return self.clip(t + 1)
        else:
            return self.clip(t - 1)


class translate(Tween):
    def __init__(self, x=0, y=0, z=0, ease=ease.linear, **kwargs):
        self.x = x
        self.y = y
        self.z = z
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if 0 <= t <= 1:
            et = self.ease(t)
            if t == 1:
                self.elements.translate(et * self.x, et * self.y, et * self.z)
            else:
                self.elements.dynamic_translate(et * self.x, et * self.y, et * self.z)
        return [self.elements]


class x(translate):
    def __init__(self, x=0, ease=ease.linear, **kwargs):
        super().__init__(x, 0, 0, ease, **kwargs)


class y(translate):
    def __init__(self, y=0, ease=ease.linear, **kwargs):
        super().__init__(0, y, 0, ease, **kwargs)


class z(translate):
    def __init__(self, z=0, ease=ease.linear, **kwargs):
        super().__init__(0, 0, z, ease, **kwargs)


class scale(Tween):
    def __init__(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5], ease=ease.linear, **kwargs):
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.anchor = anchor[:]
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if 0 <= t <= 1:
            et = self.ease(t)
            if t == 1:
                self.elements.scale(1 + et * (self.sx - 1), 1 + et * (self.sy - 1),
                                    1 + et * (self.sz - 1), self.anchor)
            else:
                self.elements.dynamic_scale(1 + et * (self.sx - 1), 1 + et * (self.sy - 1),
                                            1 + et * (self.sz - 1), self.anchor)
        return [self.elements]


class sx(scale):
    def __init__(self, sx=1, anchor=[0.5, 0.5, 0.5], ease=ease.linear, **kwargs):
        super().__init__(sx, 1, 1, anchor, ease, **kwargs)


class sy(scale):
    def __init__(self, sy=1, anchor=[0.5, 0.5, 0.5], ease=ease.linear, **kwargs):
        super().__init__(1, sy, 1, anchor, ease, **kwargs)


class sz(scale):
    def __init__(self, sz=1, anchor=[0.5, 0.5, 0.5], ease=ease.linear, **kwargs):
        super().__init__(1, 1, sz, anchor, ease, **kwargs)


class rotate(Tween):
    def __init__(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], ease=ease.linear, **kwargs):
        self.angle = angle
        self.axis = axis[:]
        self.anchor = anchor[:]
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if 0 <= t <= 1:
            et = self.ease(t)
            if t == 1:
                self.elements.rotate(et * self.angle, self.axis, self.anchor)
            else:
                self.elements.dynamic_rotate(et * self.angle, self.axis, self.anchor)
        return [self.elements]


class Common(Tween):
    def __init__(self, val, ease=ease.linear, **kwargs):
        self.p1 = None
        self.p2 = val
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if 0 <= t <= 1:
            et = self.ease(t)
            if type(self.elements) == Group:
                for element in self.elements:
                    self.update_element(element, et)
            else:
                self.update_element(self.elements, et)

        return [self.elements]


class stroke(Common):
    def update_element(self, element, et):
        self.p1 = element._stroke
        self.p2 = Element.get_rgb(self.p2)
        self.elements.stroke((1 - et) * self.p1 + et * self.p2)


class fill(Common):
    def update_element(self, element, et):
        self.p1 = element._fill
        self.p2 = Element.get_rgb(self.p2)
        self.elements.fill((1 - et) * self.p1 + et * self.p2)


class stroke_width(Common):
    def update_element(self, element, et):
        self.p1 = element._stroke_width
        self.elements.stroke_width((1 - et) * self.p1 + et * self.p2)


class stroke_dashoffset(Common):
    def update_element(self, element, et):
        self.p1 = element._stroke_dashoffset
        self.elements.stroke_dashoffset((1 - et) * self.p1 + et * self.p2)


class stroke_opacity(Common):
    def update_element(self, element, et):
        self.p1 = element._stroke_opacity
        self.elements.stroke_opacity((1 - et) * self.p1 + et * self.p2)


class fill_opacity(Common):
    def update_element(self, element, et):
        self.p1 = element._fill_opacity
        self.elements.fill_opacity((1 - et) * self.p1 + et * self.p2)


class opacity(Common):
    def update_element(self, element, et):
        self.p1 = element._opacity
        self.elements.opacity((1 - et) * self.p1 + et * self.p2)


class camera_position(Common):
    def update_element(self, element, et):
        self.p1 = element._position
        self.elements.set_position((1 - et) * self.p1 + et * self.p2)


class camera_focus(Common):
    def update_element(self, element, et):
        self.p1 = element._focus
        self.elements.set_focus((1 - et) * self.p1 + et * self.p2)
