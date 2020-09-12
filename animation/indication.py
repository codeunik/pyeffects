from ..elements import *
from ..tween import ease
from .animation import *


class focus(Animation):
    def __init__(self, color=[255, 0, 0], opacity=0.2):
        super().__init__()
        self.color = color
        self.opacity = opacity

    def animation(self):
        center = self.elements.center()
        indicator = Circle(center[0], center[1], 1).fill(self.color).opacity(self.opacity)
        self.timeline.set([(indicator.scale, (1000, 1000, 1000))])
        self.timeline.add_animation(indicator, [scale(0.001, 0.001, 0.001)],
                                    0,
                                    self.duration,
                                    ease=self.ease)
        self.timeline.remove(indicator)


class indicate(Animation):
    def __init__(self, color=[255, 0, 0], scale=1.15):
        super().__init__()
        self.color = color
        self.scale = scale

    def animation(self):
        self.timeline.add_animation(
            self.elements,
            [scale(self.scale, self.scale, self.scale),
             fill(self.color),
             stroke(self.color)],
            0,
            self.duration,
            ease=ease.there_and_back)


class rect_flash(Animation):
    def __init__(self, color=[255, 0, 0], visible_length_ratio=0.1):
        super().__init__()
        self.color = color
        self.visible_length_ratio = visible_length_ratio

    def animation(self):
        bbox = self.elements.bbox()
        x = bbox[0][0]
        y = bbox[0][1]
        width = bbox[1][0] - bbox[0][0]
        height = bbox[1][1] - bbox[0][1]
        rect_indicator = Rectangle(x, y, width, height).scale(1.1, 1.1, 1.1).stroke(
            self.color).stroke_width(3).stroke_dasharray(
                [self.visible_length_ratio, 1]).stroke_dashoffset(self.visible_length_ratio)
        self.timeline.add_animation(rect_indicator, [stroke_dashoffset(-1)],
                                    0,
                                    self.duration,
                                    ease=self.ease)
        self.timeline.remove(rect_indicator)
