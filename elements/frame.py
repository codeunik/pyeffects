import numpy as np

from .camera import Camera
from .defs import Def, Mask, ClipPath
from .element import Element
from .group import Group
from .utils import FrameConfig
import gzip
#import os

class Frame:
    def_types = ["_fill", "_stroke", "_filter", "_clip_path", "_mask"] 

    def __init__(self, width, height):
        FrameConfig.width = width
        FrameConfig.height = height
        self._header = f'''<svg width="{FrameConfig.width}" height="{FrameConfig.height}" version="1.1" viewBox="0 0 {FrameConfig.width} {FrameConfig.height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><g transform="matrix(1, 0, 0, -1, 0, 1080)">'''
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
                    if isinstance(getattr(element, _type).elements, Group):
                        for ele in getattr(element, _type).elements:
                            self._handle_defs(ele)

    def generate(self):
        z_indexed_elements = list(self.elements.values())
        z_indexed_elements.sort(key=lambda element: element.get_z_index())
        self.svg_desc = self._header

        for element in z_indexed_elements:
            bbox = element.bbox()
            if bbox[0,0] <= FrameConfig.width and 0 <= bbox[1,0] and bbox[0,1] <= FrameConfig.height and 0 <= bbox[1,1]:
                if element.get_opacity() != 0:        
                    self.svg_desc += element._draw()
                    self._handle_defs(element)

        self.svg_desc += "<defs>"
        for d in self.defs.values():
            self.svg_desc += d._str_def()
        self.svg_desc += "</defs>"

        # element.dynamic_reset()
        self.svg_desc += "</g></svg>"

        return self.svg_desc


    def save(self, path):

        with open(path, 'w') as f:
            f.write(self.svg_desc)

        # with gzip.open(path, "wb") as f:
        #     f.write(self.svg_desc.encode())
            