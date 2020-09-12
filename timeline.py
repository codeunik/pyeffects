import math
from copy import deepcopy
from uuid import uuid4

from .dynamic_data import DynamicDataIdentifier, d
from .elements import Camera, Group
from .tween import Tween, ease, translate


class Scheduler:
    def __init__(self, start=-1, end=-1, at=-1):
        self.start = start
        self.end = end
        self.at = at

    def is_time(self, t):
        if 0 <= self.start <= t:
            if t < self.end:
                return 1
            else:
                return 2
        elif 0 <= self.at <= t:
            if t < self.at:
                return 1
            else:
                return 2
        return 0

    def rel_time(self, t):
        return t - self.start


class CallBack:
    def __init__(self, func, args=tuple(), kwargs=dict()):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def exec(self):
        self.args = [
            arg.get() if isinstance(arg, DynamicDataIdentifier) else arg for arg in self.args
        ]
        self.kwargs = dict([(k, v.get() if isinstance(v, DynamicDataIdentifier) else v)
                            for k, v in self.kwargs.items()])
        self.func(*self.args, **self.kwargs)


class SetProps:
    def __init__(self, prop, info):
        self.prop = prop
        self.info = info

    def exec(self):
        self.info = [
            info.get() if isinstance(info, DynamicDataIdentifier) else info for info in self.info
        ]
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

    def remove(self, index):
        self.actions.pop(index)

    def clear(self):
        self.actions.clear()


class ElementRemover:
    def __init__(self, element_id):
        self.element_id = element_id

    def exec(self):
        Timeline.frame_elements.pop(self.element_id)


class Timeline:
    fps = 60
    frame_elements = dict()

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
        for element in Timeline.frame_elements.values():
            frame.add(element)
        while self._actions.get_action(index):
            action_scheduler, action = self._actions.get_action(index)
            is_time = action_scheduler.is_time(t)
            if is_time:
                if isinstance(action, Tween):
                    frame_elements = action.exec(t)
                    if is_time == 1:
                        for element in frame_elements:
                            frame.add(element)
                    else:
                        for element in frame_elements:
                            frame.add(element)
                            Timeline.frame_elements.setdefault(id(element), element)
                elif isinstance(action, Timeline):
                    rel_time = action_scheduler.rel_time(t)
                    action.exec(rel_time, frame)
                else:
                    action.exec()

                if is_time == 2:
                    self._actions.remove(index)
                    continue

            index += 1

        if t == self._lifetime:
            self._actions.clear()

    def add_label(self, label):
        self._labels[label] = self._cursor

    def add_animation(self,
                      elements,
                      anims,
                      delay=1,
                      duration=None,
                      label=None,
                      start=None,
                      end=None,
                      ease=ease.smooth):
        self.position_cursor(start=start, delay=delay, label=label)
        start = self._cursor
        dur = 1 if duration is None else duration
        self.position_cursor(duration=dur, end=end)
        end = self._cursor
        self._lifetime = max(self._lifetime, end)

        ease = ease if callable(ease) else ease.rate
        for anim in anims:
            anim.set_elements(elements)
            anim.set_ease(ease)
            if isinstance(anim, Tween):
                anim.timing(start, end)
                self._actions.add(Scheduler(start, end), anim)
            else:
                anim.set_timeline(self)
                if duration is not None:
                    anim.set_duration(duration)
                anim.exec(start)
        return self

    def remove(self, elements, delay=0, label=None, start=None):
        self.position_cursor(start=start, delay=delay, label=label)
        time = self._cursor
        self._actions.add(Scheduler(at=time), ElementRemover(id(elements)))
        return self

    def stagger(self,
                elements,
                anims=[Tween()],
                delay=1,
                duration=0.5,
                stagger=0.1,
                label=None,
                start=None,
                end=None,
                ease=ease.smooth):
        if isinstance(elements, Group):
            for i in range(len(elements)):
                if i == 1:
                    delay = stagger - duration
                self.add_animation(elements[i], deepcopy(anims), delay, duration, label, start, end,
                                   ease)
        else:
            self.add_animation(elements, anims, delay, duration, label, start, end, ease)

    def time(self):
        return self._cursor / self.fps

    def camera(self, anims, delay=0, duration=1, label=None, start=None, end=None, ease=None):
        return self.add_animation(Camera, anims, delay, duration, label, start, end, ease)

    def lifetime(self, t):
        self._lifetime = t

    def add_timeline(self, timeline, delay=0, label=None, start=None):
        self.position_cursor(start=start, delay=delay, label=label)
        start = self._cursor
        self._cursor += timeline._lifetime
        end = self._cursor
        self._lifetime = max(self._lifetime, end)
        self._actions.add(Scheduler(start, end), timeline)
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
        self._actions.add(Scheduler(at=time), CallBack(func, args, kwargs))
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
