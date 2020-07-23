import numpy as np

from .camera import Camera
from .defs import Def
from .element import Element
from .group import Group


class FrameConfig:
    width = 1920
    height = 1080


class Frame:
    def_types = ["_fill", "_clip_path", "_mask", "_stroke"]

    def __init__(self, width=FrameConfig.width, height=FrameConfig.height):
        self._header = f'''<svg width="{width}" height="{height}" version="1.1" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g transform="matrix(1, 0, 0, -1, 0, 1080)">'''
        self.elements = dict()
        self.defs = dict()

    def add(self, elements):
        if isinstance(elements, Group):
            for element in elements:
                self.elements.setdefault(id(element), element)

                for _type in self.def_types:
                    if isinstance(getattr(element, _type), Def):
                        self.defs.setdefault(getattr(element, _type).id, getattr(element, _type))

        elif isinstance(elements, Element):
            self.elements.setdefault(id(elements), elements)

            for _type in self.def_types:
                if isinstance(getattr(elements, _type), Def):
                    self.defs.setdefault(getattr(elements, _type).id, getattr(elements, _type))
        return self

    def save(self, path):
        z_indexed_elements = list(self.elements.values())
        z_indexed_elements.sort(key=lambda element: element.get_z_index())
        with open(path, "w") as f:
            f.write(self._header)

        with open(path, "a") as f:
            f.write("<defs>")
            for d in self.defs.values():
                f.write(d._str_def())
            f.write("</defs>")

            for element in z_indexed_elements:
                f.write(element._draw())
                element.dynamic_reset()
            f.write("</g></svg>")


class Scene:
    count = 1

    def __init__(self, *elements):
        frame = Frame()
        for element in elements:
            frame.add(element)
        frame.save(f"scene{Scene.count}.svg")
        Scene.count += 1
