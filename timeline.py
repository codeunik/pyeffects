import math
from copy import deepcopy

from .elements import Camera, Group
from .tween import Tween, ease

class Scheduler:
    def __init__(self, start=-1, end=-1):
        self.start = start
        self.end = end

    def is_time(self, t):
        if self.start <= t <= self.end:
            return 1
        return 0

    def rel_time(self, t):
        return t - self.start


# class Actions:
#     def __init__(self):
#         self.index = 0
#         self.actions = dict()

#     def add(self, scheduler, action):
#         self.actions[self.index] = (scheduler, action)
#         self.index += 1

#     def get_action(self, index):
#         if index < self.index:
#             return self.actions.get(index, True)
#         else:
#             return False

#     def remove(self, index):
#         self.actions.pop(index)

#     def clear(self):
#         self.actions.clear()


# class Actions:
#     def __init__(self):
#         self.actions = list()

#     def add(self, scheduler, action):
#         self.actions.append((scheduler, action))

#     def get_action(self, index):
#         if index < len(self.actions):
#             return self.actions[index]
#         else:
#             return False

#     def remove(self, index):
#         self.actions.pop(index)

#     def clear(self):
#         self.actions.clear()


# class Node:
#     def __init__(self, data):
#         self.data = data
#         self.prev = None
#         self.next = None

# class LinkedList:
#     def __init__(self) -> None:
#         self.head = None
#         self.tail = None
    
#     def add(self, node):
#         if self.head is None:
#             self.head = node
#         elif self.tail is None:
#             node.prev = self.head
#             self.head.next = node
#             self.tail = node
#         else:
#             node.prev = self.tail
#             self.tail.next = node
#             self.tail = node

#     def traverse(self):
#         node = self.head
#         flag = True
#         while flag:
#             yield node.data
#             node = node.next
#             if node is None:
#                 flag = False

class Timeline:
    fps = 60
    blocklist = dict()

    def __init__(self, fps=None):
        if fps:
            Timeline.fps = fps
        
        self.round_ndigits = len(f'{Timeline.fps}')

        self._cursor = 0
        self._lifetime = 0
        self._actions = dict()
        self._labels = dict()

    def exec(self, t):
        [action.exec(t) for action in self._actions.get(t, [])]
            

        # index = 0
        # while self._actions.get_action(index):
        #     action = self._actions.get_action(index)
        #     if type(action) == tuple:
        #         action_scheduler, action = action
        #         is_time = action_scheduler.is_time(t)
        #         if is_time:
        #             action.exec(t)
        #     index += 1

    def add_label(self, label):
        self._labels[label] = self._cursor

    def add_animation(self,
                      elements,
                      anim,
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
        print(start, end)

        anim.set_elements(elements)
        anim.set_ease(ease)
        if isinstance(anim, Tween):
            anim.timing(start, end, Timeline.fps)
            for i in range(start, end+1):
                self._actions.setdefault(i, list())
                self._actions[i].append(anim)
        else:
            anim.set_timeline(self)
            anim.set_fps(Timeline.fps)
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

    def lifetime(self, t):
        self._lifetime = t

    def position_cursor(self, start=None, end=None, delay=None, duration=None, label=None):
        if label:
            if self._labels.get(label, None):
                self._cursor = self._labels[label]
            else:
                self._labels[label] = self._cursor
        if start:
            start = int(round(start, self.round_ndigits) * Timeline.fps)
            self._cursor = start
        if delay:
            delay = int(round(delay, self.round_ndigits) * Timeline.fps)
            self._cursor = max(self._cursor + delay, 0)

        if duration:
            duration = int(round(duration, self.round_ndigits) * Timeline.fps)
            self._cursor = (self._cursor + duration)
        if end:
            end = int(round(end, self.round_ndigits) * Timeline.fps)
            self._cursor = end
