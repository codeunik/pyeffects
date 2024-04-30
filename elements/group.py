from copy import deepcopy

import numpy as np

from .element import Element
from .place import Place

class Group(list, Place):
    def __init__(self, *group):
        list.__init__(self)
        self.add(*group)

    def add(self, *elements):
        for item in Group._flatten(elements):
            self.append(item)

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def _flatten(target):
        for item in target:
            if isinstance(item, Element):
                yield item
            elif isinstance(item, Group):
                yield from Group._flatten(item)

    def continuous_subpaths(self):
        continuous_subpaths = []
        for element in self:
            continuous_subpaths.append(element.continuous_subpaths())
        
        return Group(*continuous_subpaths)


    def bbox(self):
        x_min_list = []
        y_min_list = []
        z_min_list = []
        x_max_list = []
        y_max_list = []
        z_max_list = []
        for element in self:
            element_bbox = element.bbox()
            x_min_list.append(element_bbox[0][0])
            y_min_list.append(element_bbox[0][1])
            z_min_list.append(element_bbox[0][2])
            x_max_list.append(element_bbox[1][0])
            y_max_list.append(element_bbox[1][1])
            z_max_list.append(element_bbox[1][2])
        
        group_x_min = min(x_min_list)
        group_y_min = min(y_min_list)
        group_z_min = min(z_min_list)
        group_x_max = max(x_max_list)
        group_y_max = max(y_max_list)
        group_z_max = max(z_max_list)
        
        return np.array([[group_x_min, group_y_min, group_z_min, 1.0],
                         [group_x_max, group_y_max, group_z_max, 1.0]])

    def anchor_point(self, anchor=[0.5, 0.5]):
        bbox = self.bbox()
        anchor2 = np.ones(4)
        anchor2[:len(anchor)] = anchor
        return (bbox[0] * (1 - anchor2) + anchor2 * bbox[1])[:len(anchor)] 

    def center(self):
        return self.bbox().sum(axis=0) / 2

    def reset(self):
        for element in self:
            element.static = np.eye(3, dtype=np.float)
        return self

    def translate(self, x=0, y=0, z=0):
        for element in self:
            element.static = element.translation_matrix(x, y, z).dot(element.static)
        return self

    def scale(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        for element in self:
            element.static = element.scale_matrix(sx, sy, sz, abs_anchor[:3]).dot(element.static)
        return self

    def rotate(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)

        for element in self:
            element.static = element.rotation_matrix(angle, axis,
                                                     abs_anchor[:3]).dot(element.static)
        return self

    def matrix(self, mat):
        for element in self:
            element.static = mat.dot(element.static)
        return self

    def dynamic_reset(self):
        for element in self:
            element.static = np.eye(3, dtype=np.float)
        return self

    def dynamic_translate(self, x=0, y=0, z=0):
        for element in self:
            element.dynamic = element.translation_matrix(x, y, z).dot(element.dynamic)
        return self

    def dynamic_scale(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        for element in self:
            element.dynamic = element.scale_matrix(sx, sy, sz, abs_anchor[:3]).dot(element.dynamic)
        return self

    def dynamic_rotate(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)

        for element in self:
            element.dynamic = element.rotation_matrix(angle, axis,
                                                      abs_anchor[:3]).dot(element.dynamic)
        return self

    def dynamic_matrix(self, mat):
        for element in self:
            element.dynamic = mat.dot(element.dynamic)
        return self

    def z_index(self, z_index):
        for element in self:
            element.z_index(z_index)
        return self

    def stroke_width(self, stroke_width):
        for element in self:
            element.stroke_width(stroke_width)
        return self

    def stroke(self, color):
        for element in self:
            element.stroke(color)
        return self

    def fill(self, color):
        for element in self:
            element.fill(color)
        return self

    def opacity(self, opacity):
        for element in self:
            element.opacity(opacity)
        return self

    def fill_opacity(self, fill_opacity):
        for element in self:
            element.fill_opacity(fill_opacity)
        return self

    def stroke_opacity(self, stroke_opacity):
        for element in self:
            element.stroke_opacity(stroke_opacity)
        return self

    def stroke_linecap(self, stroke_linecap):
        for element in self:
            element.stroke_linecap(stroke_linecap)
        return self

    def stroke_linejoin(self, stroke_linejoin):
        for element in self:
            element.stroke_linejoin(stroke_linejoin)
        return self

    def stroke_dasharray(self, stroke_dasharray):
        for element in self:
            element.stroke_dasharray(stroke_dasharray)
        return self

    def fill_rule(self, fill_rule):
        for element in self:
            element.fill_rule(fill_rule)
        return self

    def stroke_miterlimit(self, stroke_miterlimit):
        for element in self:
            element.stroke_miterlimit(stroke_miterlimit)
        return self

    def stroke_dashoffset(self, stroke_dashoffset):
        for element in self:
            element.stroke_dashoffset(stroke_dashoffset)
        return self
    
    def mask(self, mask):
        for element in self:
            element.mask(mask)
        return self
    
    def filter(self, f):
        for element in self:
            element.filter(f)
        return self
