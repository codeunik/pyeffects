from ..tween import *


class Animation:
    def __init__(self):
        self.duration = 1

    def set_elements(self, elements):
        self.elements = elements

    def set_ease(self, ease):
        self.ease = ease

    def set_timeline(self, timeline):
        self.timeline = timeline

    def set_duration(self, duration):
        self.duration = duration

    def set_fps(self, fps):
        self.fps = fps

    def get_durations(self, weights):
        a = self.fps * self.duration * weights / np.sum(weights)
        a = np.round(a.cumsum())
        durations = np.zeros_like(a)
        durations[0] = a[0]
        durations[1:] = a[1:] - a[:-1]
        durations = durations / self.fps
        return durations
    
    def exec(self, start):
        self.timeline._cursor = start
        self.animation()
