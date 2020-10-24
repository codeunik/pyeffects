import math
from copy import deepcopy

from .dynamic_data import DynamicDataIdentifier
from .elements import Camera, Group
from .tween import Tween, ease


class Scheduler:
    def __init__(self, start=-1, end=-1, at=-1):
        self.start = start
        self.end = end
        self.at = at

    def is_time(self, t):
        if 0 <= self.start <= t:
            return 1
        elif 0 <= self.at <= t:
            if t == self.at:
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

class Block:
    def __init__(self, element):
        self.element = element

    def exec(self):
        element_id = id(self.element.get()) if isinstance(self.element, DynamicDataIdentifier) else id(self.element)
        Timeline.blocklist[element_id] = 0

class Unblock:
    def __init__(self, element):
        self.element = element

    def exec(self):
        element_id = id(self.element.get()) if isinstance(self.element, DynamicDataIdentifier) else id(self.element)
        Timeline.blocklist.pop(element_id, None)


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


class Timeline:
    fps = 24
    blocklist = dict()

    def __init__(self, fps=None):
        if fps:
            Timeline.fps = fps

        self._cursor = 0
        self._lifetime = 0
        self._actions = Actions()
        self._labels = dict()
        self._time_scale = 1

    def exec(self, t, frame):
        index = 0
        while self._actions.get_action(index):
            action_scheduler, action = self._actions.get_action(index)
            is_time = action_scheduler.is_time(t)
            if isinstance(action, Tween):
                if is_time:
                    frame_elements = action.exec(t)
                    for element in frame_elements:
                        if Timeline.blocklist.get(id(element), 1):
                            frame.add(element)
            elif isinstance(action, Timeline):
                if is_time:
                    rel_time = action_scheduler.rel_time(t)
                    action.exec(rel_time, frame)
            elif isinstance(action, CallBack) or isinstance(action, SetProps):
                if is_time == 1:
                    action.exec()
                elif is_time == 2:
                    self._actions.remove(index)
                    continue

            index += 1


    def add_label(self, label):
        self._labels[label] = self._cursor

    def block(self, elements, delay=0, label=None, start=None):
        self.position_cursor(start=start, delay=delay, label=label)
        time = self._cursor
        self._actions.add(Scheduler(at=time), Block(elements))
        return self

    def unblock(self, elements, delay=0, label=None, start=None):
        self.position_cursor(start=start, delay=delay, label=label)
        time = self._cursor
        self._actions.add(Scheduler(at=time), Unblock(elements))
        return self

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
        #print(start, end)
        ease = ease if callable(ease) else ease.rate
        for anim in anims:
            anim.set_elements(elements)
            anim.set_ease(ease)
            if isinstance(anim, Tween):
                anim.timing(start, end, Timeline.fps)
                self._actions.add(Scheduler(start, end), anim)
            else:
                anim.set_timeline(self)
                if duration is not None:
                    anim.set_duration(duration)
                anim.exec(start)
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
            delay = math.ceil(delay * Timeline.fps / self._time_scale) if delay >= 0 else math.floor(delay * Timeline.fps / self._time_scale)
            self._cursor = max(self._cursor + delay, 0)

        if duration:
            duration = math.ceil(duration * Timeline.fps / self._time_scale)
            self._cursor = (self._cursor + duration)
        if end:
            end = math.ceil(end * Timeline.fps / self._time_scale)
            self._cursor = end
