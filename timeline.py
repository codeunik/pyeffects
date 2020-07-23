import math

from .elements import Camera
from .tween import Tween


class Scheduler:
    def __init__(self, start=-1, at=-1):
        self.start = start
        self.at = at

    def is_time(self, t):
        if 0 <= self.start <= t:
            return True
        elif 0 <= self.at == t:
            return True
        return False

    def rel_time(self, t):
        return t - self.start


class CallBack:
    def __init__(self, timeline, func, args=tuple(), kwargs=dict()):
        self.timeline = timeline
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def exec(self):
        Timeline.func = self.func
        self.timeline.func(*self.args, **self.kwargs)


class SetProps:
    def __init__(self, prop, info):
        self.prop = prop
        self.info = info

    def exec(self):
        self.prop(*self.info)


class Actions:
    def __init__(self):
        self.actions = list()

    def add(self, scheduler, action):
        self.actions.append((scheduler, action))

    def get_action(self, index):
        if index < len(self.actions):
            return self.actions[index]
        else:
            return False

    def remove(self):
        self.actions.clear()


class Timeline:
    fps = 60
    data = dict()

    def __init__(self, fps=None):
        if fps:
            Timeline.fps = fps
        # if is_master:
        #     # This timeline should be used for adding dynamic tweens
        #     Timeline.master = self

        self._cursor = 0
        self._lifetime = 0
        self._actions = Actions()
        self._labels = dict()
        self._time_scale = 1

    def exec(self, t, frame):
        index = 0
        while self._actions.get_action(index):
            action_scheduler, action = self._actions.get_action(index)
            if action_scheduler.is_time(t):
                if isinstance(action, Tween):
                    frame_elements = action.exec(t)
                    for element in frame_elements:
                        frame.add(element)
                elif isinstance(action, Timeline):
                    rel_time = action_scheduler.rel_time(t)
                    action.exec(rel_time, frame)
                else:
                    action.exec()
            index += 1
        if t == self._lifetime:
            self._actions.remove()

    def add_label(self, label):
        self._labels[label] = self._cursor

    def add_tween(self,
                  elements,
                  tweens,
                  duration=0.5,
                  delay=0,
                  label=None,
                  start=None,
                  end=None,
                  ease=None):

        self.position_cursor(start=start, delay=delay, label=label)
        start = self._cursor
        self.position_cursor(duration=duration, end=end)
        end = self._cursor
        self._lifetime = max(self._lifetime, end)

        for tween in tweens:
            if elements:
                tween.set_elements(elements)
            if ease:
                tween.set_ease(ease)
            tween.timing(start, end)
            self._actions.add(Scheduler(start), tween)
        return self

    def camera(self, tweens, duration=0.5, delay=0, label=None, start=None, end=None, ease=None):
        return self.add_tween(Camera, tweens, duration, delay, label, start, end, ease)

    def lifetime(self, t):
        self._lifetime = t

    def add_timeline(self, timeline, delay=0, label=None, start=None):
        self.position_cursor(start=start, delay=delay, label=label)
        start = self._cursor
        self._cursor += timeline._lifetime
        end = self._cursor
        self._lifetime = max(self._lifetime, end)
        self._actions.add(Scheduler(start), timeline)
        return self

    def set(self, update_info, start=None, delay=0, label=None):
        self.position_cursor(start=start, delay=delay, label=label)
        time = self._cursor
        for prop, info in update_info:
            if type(info) != list and type(info) != tuple:
                info = [info]
            self._actions.add(Scheduler(at=time), SetProps(prop, info))
        return self

    def call(self, func, args=tuple(), kwargs=dict(), start=None, delay=0, label=None):
        self.position_cursor(start=start, delay=delay, label=label)
        time = self._cursor
        self._actions.add(Scheduler(at=time), CallBack(self, func, args, kwargs))
        return self

    def time_scale(self, val):
        self._time_scale = val

    def repeat(self, n):
        for i in range(n):
            self.add_timeline(self)
        return self

    def position_cursor(self, start=None, end=None, delay=None, duration=None, label=None):
        if label:
            if self._labels.get(label, None):
                self._cursor = self._labels[label]
            else:
                self._labels[label] = self._cursor
        if start:
            start = math.ceil(start * Timeline.fps / self._time_scale)
            self._cursor = start
        if delay:
            delay = math.ceil(delay * Timeline.fps / self._time_scale)
            self._cursor += delay

        if duration:
            duration = math.ceil(duration * Timeline.fps / self._time_scale)
            self._cursor = (self._cursor + duration)
        if end:
            end = math.ceil(end * Timeline.fps / self._time_scale)
            self._cursor = end
