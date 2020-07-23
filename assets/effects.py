from copy import deepcopy

from ..tween import *
from .draw_svg import draw_svg


def stagger(timeline, group, tweens, duration=0.5, stagger=0.1,\
            delay=0, label=None, start=None, end=None, ease=None):
    for i in range(len(group)):
        if i == 1:
            delay = stagger - duration

        timeline.add_tween(group[i], deepcopy(tweens),\
                           duration, delay, label, start, end, ease)


def anim_stroke(timeline, group, duration=0.5, stagger_duration=0.1,\
                delay=0, label=None, start=None, end=None, ease=None):
    stagger(timeline, group,\
            [draw_svg(0, 0, 0, 1), fill_opacity(1)],\
            duration, stagger_duration, delay, label, start, end, ease)


def reverse_anim_stroke(timeline, group, duration=0.5, stagger_duration=0.1,\
                        delay=0, label=None, start=None, end=None, ease=None):
    stagger(timeline, group,\
            [draw_svg(0, 1, 0, 0), fill_opacity(0)],\
            duration, stagger_duration, delay, label, start, end, ease)


def fade_in(timeline, group, delay=0, label=None,\
            start=None, end=None, ease=None):
    timeline.add_tween(group, [opacity(1)], 0.33, delay, label, start, end, ease)\


def fade_out(timeline, group, delay=0, label=None,\
             start=None, end=None, ease=None):
    timeline.add_tween(group, [opacity(0)], 0.33, delay, label, start, end, ease)\
