import numpy as np

from ..dynamic_data import DynamicDataIdentifier
from ..elements.element import Element
from ..elements.group import Group
from ..elements.utils import Color
import os
import hashlib

class Tween:
    def __init__(self, on_update=None, kwargs_dict=None):

        self.on_update = on_update
        self.on_update_kwargs = kwargs_dict

        self.start_frame = 0
        self.end_frame = -1
        self.fps = None
        self.dynamic_data_flag = 1

    def set_elements(self, elements):
        self.elements = elements

    def set_ease(self, ease):
        self.ease = ease

    def exec(self, frame_number):
        if self.dynamic_data_flag:
            for var in dir(self):
                if isinstance(getattr(self, var), DynamicDataIdentifier):
                    setattr(self, var, getattr(self, var).get())
            self.dynamic_data_flag = 0

        if self.on_update:
            self.on_update(self, **self.on_update_kwargs)

        return self.update(self.rel_frame_number(frame_number))

    def update(self, rel_frame_number):
        return [self.elements]

    def rel_frame_number(self, frame_number):
        return frame_number - self.start_frame

    def progress(self, rel_frame_number):
        if self.start_frame == self.end_frame:
            return 1
        return rel_frame_number / (self.end_frame - self.start_frame)

    def timing(self, start_frame, end_frame, fps):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.fps = fps


class translate(Tween):
    def __init__(self, x=0, y=0, z=0, **kwargs):
        self.x = x
        self.y = y
        self.z = z
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        t = self.progress(rel_frame_number)
        et = self.ease(t)
        if t == 1:
            self.elements.translate(et * self.x, et * self.y, et * self.z)
        else:
            self.elements.dynamic_translate(et * self.x, et * self.y, et * self.z)
        return [self.elements]


class x(translate):
    def __init__(self, x=0, **kwargs):
        super().__init__(x, 0, 0, **kwargs)


class y(translate):
    def __init__(self, y=0, **kwargs):
        super().__init__(0, y, 0, **kwargs)


class z(translate):
    def __init__(self, z=0, **kwargs):
        super().__init__(0, 0, z, **kwargs)


class scale(Tween):
    def __init__(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5], **kwargs):
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.anchor = anchor[:]
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        t = self.progress(rel_frame_number)
        et = self.ease(t)
        if t == 1:
            self.elements.scale(1 + et * (self.sx - 1), 1 + et * (self.sy - 1),
                                1 + et * (self.sz - 1), self.anchor)
        else:
            self.elements.dynamic_scale(1 + et * (self.sx - 1), 1 + et * (self.sy - 1),
                                        1 + et * (self.sz - 1), self.anchor)
        return [self.elements]


class sx(scale):
    def __init__(self, sx=1, anchor=[0.5, 0.5, 0.5], **kwargs):
        super().__init__(sx, 1, 1, anchor, **kwargs)


class sy(scale):
    def __init__(self, sy=1, anchor=[0.5, 0.5, 0.5], **kwargs):
        super().__init__(1, sy, 1, anchor, **kwargs)


class sz(scale):
    def __init__(self, sz=1, anchor=[0.5, 0.5, 0.5], **kwargs):
        super().__init__(1, 1, sz, anchor, **kwargs)


class rotate(Tween):
    def __init__(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], **kwargs):
        self.angle = angle
        self.axis = axis[:]
        self.anchor = anchor[:]
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        t = self.progress(rel_frame_number)
        et = self.ease(t)
        if t == 1:
            self.elements.rotate(et * self.angle, self.axis, self.anchor)
        else:
            self.elements.dynamic_rotate(et * self.angle, self.axis, self.anchor)
        return [self.elements]


class Common(Tween):
    def __init__(self, val, **kwargs):
        self.p1 = None
        self.p2 = val
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        t = self.progress(rel_frame_number)
        et = self.ease(t)
        if type(self.elements) == Group:
            for element in self.elements:
                self.update_element(element, et)
        else:
            self.update_element(self.elements, et)

        return [self.elements]


class stroke(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._stroke
        self.p2 = np.array(self.p2)
        self.elements.stroke((1 - et) * self.p1 + et * self.p2)


class fill(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._fill
        self.p2 = np.array(self.p2)
        self.elements.fill((1 - et) * self.p1 + et * self.p2)


class stroke_width(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._stroke_width
        self.elements.stroke_width((1 - et) * self.p1 + et * self.p2)


class stroke_dasharray(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._stroke_dashoffset
        self.p2 = np.array(self.p2)
        self.elements.stroke_dashoffset((1 - et) * self.p1 + et * self.p2)


class stroke_dashoffset(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._stroke_dashoffset
        self.elements.stroke_dashoffset((1 - et) * self.p1 + et * self.p2)


class stroke_opacity(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._stroke_opacity
        self.elements.stroke_opacity((1 - et) * self.p1 + et * self.p2)


class fill_opacity(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._fill_opacity
        self.elements.fill_opacity((1 - et) * self.p1 + et * self.p2)


class opacity(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._opacity
        self.elements.opacity((1 - et) * self.p1 + et * self.p2)


class draw(Tween):
    def __init__(self, start=[0, 1], end=[1, 0], **kwargs):
        self.start = np.array(start)
        self.end = np.array(end)
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        t = self.progress(rel_frame_number)
        et = self.ease(t)
        self.elements.stroke_dasharray((1 - et) * self.start + et * self.end)
        return [self.elements]

class play(Tween):
    def __init__(self, start_sec=0, speed=1, **kwargs):
        self.start_sec = start_sec
        self.speed = speed
        super().__init__(**kwargs)

    def update(self, rel_frame_number):
        if rel_frame_number == 0:
            video_duration = self.speed * (self.end_frame - self.start_frame)/self.fps
            video_fps = self.fps / self.speed
            self.file_hash = hashlib.md5(
                bytes(f"{self.elements.filepath, self.start_sec, self.speed, video_duration}", encoding="utf-8")).hexdigest()
            # ffmpeg -i mov.mp4 -r 60 -f image2 image-%07d.png
            os.system(f'mkdir -p /tmp/{self.file_hash} '
                      + f'&& ffmpeg -ss {self.start_sec} -i {self.elements.filepath} -t {video_duration}'
                      + f'-r {video_fps} -f image2 /tmp/{self.file_hash}/%d.png')

        self.elements.set_image(f'/tmp/{self.file_hash}/{rel_frame_number+1}.png')
        return [self.elements]

class camera_position(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._position
        self.elements.set_position((1 - et) * self.p1 + et * self.p2)

class camera_focus(Common):
    def update_element(self, element, et):
        if self.p1 is None:
            self.p1 = element._focus
        self.elements.set_focus((1 - et) * self.p1 + et * self.p2)
