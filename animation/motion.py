from .animation import *


class swirl_to_pos(Animation):
    def __init__(self, translate=[0, 0, 0], rotate=-360, scale=[1, 1, 1], duration=1, stagger=0.1):
        super().__init__()
        self.translate = translate
        self.rotate = rotate
        self.scale = scale
        self.duration = duration
        self.stagger = stagger

    def animation(self):
        total_elements = len(self.elements) if isinstance(self.elements, Group) else 1
        elements_copy = self.elements.copy().scale(*self.scale).translate(*self.translate)
        for i in range(total_elements):
            element = self.elements[i] if isinstance(self.elements, Group) else self.elements
            element_copy = elements_copy[i] if isinstance(self.elements, Group) else elements_copy
            new_pos = element.to_relative_of(element_copy, [0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
            delay = 0 if i == 0 else self.stagger - self.duration
            self.timeline.add_animation(
                element, [translate(*new_pos),
                          rotate(-360), scale(*self.scale)],
                delay,
                self.duration,
                ease=self.ease)
