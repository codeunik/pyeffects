import numpy as np

from .camera import Camera
from .defs import Def, Mask, ClipPath
from .element import Element
from .group import Group


class FrameConfig:
    width = 1920
    height = 1080


class Frame:
    def_types = ["_fill", "_stroke", "_filter", "_clip_path", "_mask"]

    def __init__(self, width=FrameConfig.width, height=FrameConfig.height):
        self._header = f'''<svg width="{width}" height="{height}" version="1.1" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g transform="matrix(1, 0, 0, -1, 0, 1080)">'''
        self.groups = dict()
        self.elements = dict()
        self.defs = dict()

    def add(self, elements):
        if isinstance(elements, Group):
            if self.groups.get(id(elements), True):
                self.groups.setdefault(id(elements), False)
                for element in elements:
                    self.elements.setdefault(id(element), element)
        elif isinstance(elements, Element):
            self.elements.setdefault(id(elements), elements)

        return self

    def _handle_defs(self, element):
        for _type in self.def_types:
            if isinstance(getattr(element, _type), Def):
                self.defs.setdefault(getattr(element, _type).id, getattr(element, _type))
                if isinstance(getattr(element, _type), Mask) or isinstance(getattr(element, _type), ClipPath):
                    self._handle_defs(getattr(element, _type).element)

    def save(self, path):
        z_indexed_elements = list(self.elements.values())
        z_indexed_elements.sort(key=lambda element: element.get_z_index())
        svg_desc = self._header

        for element in z_indexed_elements:
            svg_desc += element._draw()
            self._handle_defs(element)

        svg_desc += "<defs>"
        for d in self.defs.values():
            svg_desc += d._str_def()
        svg_desc += "</defs>"

        #element.dynamic_reset()
        svg_desc += "</g></svg>"

        with open(path, "w") as f:
            f.write(svg_desc)

class Scene:
    count = 1

    def __init__(self, *elements):
        frame = Frame()
        for element in elements:
            frame.add(element)
        frame.save(f"scene{Scene.count}.svg")
        Scene.count += 1
