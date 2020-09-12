from .animation import *


class draw_and_then_fill(Animation):
    def __init__(self, element_duration=0.25):
        super().__init__()
        self.element_duration = element_duration

    def animation(self):
        total_elements = len(self.elements) if isinstance(self.elements, Group) else 1
        self.duration = (total_elements * self.element_duration) / (1 + 0.075 * total_elements)
        self.timeline.set([(self.elements.fill_opacity, 0)])
        stagger = self.duration / (4 * (total_elements - 1))
        t1 = self.timeline.time()
        self.timeline.stagger(self.elements, [draw([0, 1], [1, 0])],
                              0,
                              self.duration / 4,
                              stagger,
                              ease=self.ease)
        self.timeline.add_animation(self.elements, [fill_opacity(1)],
                                    0,
                                    self.duration / 2,
                                    ease=self.ease)


class write(Animation):
    def __init__(self, element_duration=0.25):
        super().__init__()
        self.element_duration = element_duration

    def animation(self):
        total_elements = len(self.elements) if isinstance(self.elements, Group) else 1
        self.duration = (total_elements * self.element_duration) / (1 + 0.075 * total_elements)
        element_duration = 3 * self.duration / (total_elements + 8)
        self.timeline.set([(self.elements.fill_opacity, 0), (self.elements.stroke_opacity, 1)])
        stagger = element_duration / 3

        t1 = self.timeline.time()
        self.timeline.stagger(self.elements, [draw([0, 1], [1, 0])],
                              0,
                              element_duration,
                              stagger,
                              ease=self.ease)
        t2 = self.timeline.time()

        self.timeline.stagger(self.elements, [fill_opacity(1)],
                              t1 - t2 + element_duration,
                              element_duration,
                              stagger,
                              ease=self.ease)
        t3 = self.timeline.time()

        self.timeline.stagger(self.elements, [stroke_opacity(0)],
                              t1 - t3 + 2 * element_duration,
                              element_duration,
                              stagger,
                              ease=self.ease)


class grow(Animation):
    def __init__(self, anchor=[0.5, 0.5, 0.5], from_point=None):
        super().__init__()
        self.anchor = anchor
        self.from_point = from_point

    def animation(self):
        def get_info(elements, anchor, from_point):
            if from_point:
                anchor = elements.anchor(elements, np.array([*anchor, 1.0]))
                from_point = np.array(from_point)
                trans = from_point[:3] - anchor[:3]
                elements.translate(*trans)
                trans = -trans
            else:
                trans = [0, 0, 0]
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info, (self.elements, self.anchor, self.from_point))
        self.timeline.set([(self.elements.scale, (0.001, 0.001, 0.001, self.anchor))])
        self.timeline.add_animation(
            self.elements, [translate(d.x, d.y, d.z),
                            scale(1000, 1000, 1000, self.anchor)],
            0,
            self.duration,
            ease=self.ease)


class shrink(Animation):
    def __init__(self, anchor=[0.5, 0.5, 0.5], to_point=None):
        super().__init__()
        self.anchor = anchor
        self.to_point = to_point

    def animation(self):
        def get_info(elements, anchor, to_point):
            if to_point:
                anchor = elements.anchor(elements, np.array([*anchor, 1.0]))
                to_point = np.array(from_point)
                trans = to_point[:3] - anchor[:3]
            else:
                trans = [0, 0, 0]
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info, (self.elements, self.anchor, self.to_point))
        self.timeline.add_animation(
            self.elements, [translate(d.x, d.y, d.z),
                            scale(0.0001, 0.0001, 0.0001, self.anchor)],
            0,
            self.duration,
            ease=self.ease)


class fade_in(Animation):
    def __init__(self, from_direction=5, from_point=None, from_scale=1):
        super().__init__()
        self.from_direction = from_direction
        self.from_point = from_point
        self.from_scale = from_scale

    def animation(self):
        def get_info(timeline, elements, from_direction, from_point):
            if from_point:
                center = elements.center()
                from_point = np.array(from_point)
                trans = from_point[:3] - center[:3]
            else:
                bbox = elements.bbox()
                width = (bbox[1][0] - bbox[0][0]) / 2
                height = (bbox[1][1] - bbox[0][1]) / 2
                trans = [0, 0, 0] if from_direction == 5\
                    else [0, height, 0] if from_direction == 8\
                    else [0, -height, 0] if from_direction == 2\
                    else [-width, 0, 0] if from_direction == 4\
                    else [width, 0, 0] if from_direction == 6\
                    else [-width, -height, 0] if from_direction == 1\
                    else [width, -height, 0] if from_direction == 3\
                    else [-width, height, 0] if from_direction == 7\
                    else [width, height, 0] if from_direction == 9\
                    else [0, 0, 0]
                trans = np.array(trans)
            elements.translate(*trans)
            trans = -trans
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info,
                           (self.timeline, self.elements, self.from_direction, self.from_point))
        self.timeline.set([(self.elements.opacity, (0)),
                           (self.elements.scale, (self.from_scale, self.from_scale,
                                                  self.from_scale))])
        self.timeline.add_animation(self.elements, [
            translate(d.x, d.y, d.z),
            opacity(1),
            scale(1 / self.from_scale, 1 / self.from_scale, 1 / self.from_scale)
        ],
                                    0,
                                    self.duration,
                                    ease=self.ease)


class fade_out(Animation):
    def __init__(self, to_direction=5, to_point=None, to_scale=1):
        super().__init__()
        self.to_direction = to_direction
        self.to_point = to_point
        self.to_scale = to_scale

    def animation(self):
        def get_info(timeline, elements, to_direction, to_point):
            if to_point:
                center = elements.center()
                to_point = np.array(to_point)
                trans = to_point[:3] - center[:3]
            else:
                bbox = elements.bbox()
                width = (bbox[1][0] - bbox[0][0]) / 2
                height = (bbox[1][1] - bbox[0][1]) / 2
                trans = [0, 0, 0] if to_direction == 5\
                    else [0, height, 0] if to_direction == 8\
                    else [0, -height, 0] if to_direction == 2\
                    else [-width, 0, 0] if to_direction == 4\
                    else [width, 0, 0] if to_direction == 6\
                    else [-width, -height, 0] if to_direction == 1\
                    else [width, -height, 0] if to_direction == 3\
                    else [-width, height, 0] if to_direction == 7\
                    else [width, height, 0] if to_direction == 9\
                    else [0, 0, 0]
                trans = np.array(trans)
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info,
                           (self.timeline, self.elements, self.to_direction, self.to_point))
        self.timeline.add_animation(self.elements, [
            translate(d.x, d.y, d.z),
            opacity(0),
            scale(self.to_scale, self.to_scale, self.to_scale)
        ],
                                    0,
                                    self.duration,
                                    ease=self.ease)
