import numpy as np

from ..dynamic_data import DynamicDataIdentifier, d
from ..timeline import Timeline
from ..tween import *


class Animation:
    def __init__(self):
        self.duration = 1
        self.flag = 1

    def set_elements(self, elements):
        self.elements = elements

    def set_ease(self, ease):
        self.ease = ease

    def set_timeline(self, timeline):
        self.timeline = timeline

    def set_duration(self, duration):
        self.duration = duration

    def get_duration(self):
        return self.duration

    def exec(self, start):
        if self.flag:
            for var in dir(self):
                if isinstance(getattr(self, var), DynamicDataIdentifier):
                    setattr(self, var, getattr(self, var).get())
            self.flag = 0
        self.timeline._cursor = start
        self.animation()
