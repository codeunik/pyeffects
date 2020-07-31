from copy import deepcopy

import numpy as np

from ._component_manipulation import (_replace_by_beziers, _split_bezier,
                                      _update_comp_len_list)
from .camera import Camera
from .defs import LinearGradient, RadialGradient
from .element import Element
from .group import Group
from .light import Light
from .svgpathtools import Path as SVGPath
from .svgpathtools import Arc, CubicBezier, Line, QuadraticBezier, parse_path
from .utils import unit_vector


class Path(Element):
    def __init__(self, data=None, has_shading=False):
        self._data_3d = []
        self._index_map = dict()
        self._has_shading = has_shading
        self._bbox = None
        self._transformed_points = None
        self._vertex_avg = None
        if data is not None:
            self.set_segments(data)
        Element.__init__(self)

    def set_segments(self, data):
        self._data_3d = []
        self._index_map = dict()
        self._transformed_points = None
        self._vertex_avg = None
        if type(data) == str:
            self._data_2d = SVGPath(*_replace_by_beziers(parse_path(data)))
        elif type(data) == SVGPath:
            self._data_2d = SVGPath(*_replace_by_beziers(data))
        else:
            self._data_2d = SVGPath(*data)

        self._convert_2d_to_3d()
        self._create_bbox()
        return self

    def has_shading(self, has_shading):
        self._has_shading = has_shading
        return self

    def get_z_index(self):
        self._get_vertex_avg()
        if self._z_index is None:
            return self._vertex_avg[2]
        else:
            return self._z_index

    def _create_bbox(self):
        x_min = self._data_3d[:-1, 0].min()
        y_min = self._data_3d[:-1, 1].min()
        z_min = self._data_3d[:-1, 2].min()
        x_max = self._data_3d[:-1, 0].max()
        y_max = self._data_3d[:-1, 1].max()
        z_max = self._data_3d[:-1, 2].max()
        self._bbox = np.array([
            [x_min, y_min, z_min, 1.0],  # 0, 0, 0
            [x_min, y_min, z_max, 1.0],  # 0, 0, 1
            [x_min, y_max, z_min, 1.0],  # 0, 1, 0
            [x_min, y_max, z_max, 1.0],  # 0, 1, 1
            [x_max, y_min, z_min, 1.0],  # 1, 0, 0
            [x_max, y_min, z_max, 1.0],  # 1, 0, 1
            [x_max, y_max, z_min, 1.0],  # 1, 1, 0
            [x_max, y_max, z_max, 1.0],  # 1, 1, 1
        ])

    def _get_transformed_points(self):
        self._transformed_points = self.transform_3d().dot(self._data_3d.T).T

    def _get_vertex_avg(self):
        self._get_transformed_points()
        self._vertex_avg = sum(self._transformed_points[:-1]) / (
            len(self._transformed_points) - 1)

    def _border_length(self):
        self._convert_3d_to_2d()
        return self._data_2d.length()

    def _str_fill(self):
        if self._has_shading:
            if isinstance(self._fill, np.ndarray):
                self._get_vertex_avg()
                face_to_light = unit_vector(Light.get_position() -
                                            self._vertex_avg)
                face_normal = unit_vector(self._transformed_points[-1])
                ambient_coeff = 0.33
                diffuse_coeff = 0.67 * (abs(face_normal[:3].dot(
                    face_to_light[:3])))
                color = self._fill * (ambient_coeff + diffuse_coeff)
                return f'fill="rgb{tuple(color)}"'
        if isinstance(self._fill, LinearGradient):
            return f'fill="url(#{self._fill.id})"'
        elif isinstance(self._fill, RadialGradient):
            return f'fill="url(#{self._fill.id})"'
        return f'fill="{self._str_color(self._fill)}"'

    def _draw(self):
        self._convert_3d_to_2d()
        s = f'<path d="{self._data_2d.d()}" '
        s += super()._draw()
        s += "></path>"
        return s

    def _convert_2d_to_3d(self):
        def c2v(z):
            return np.array([z.real, z.imag, 0, 1])

        temp_map = dict()
        index = 0
        comp_index = 0
        for comp in self._data_2d:
            point_index = 0
            for point in comp:
                temp_index = temp_map.get(point, -1)
                if temp_index + 1:
                    self._index_map[(comp_index, point_index)] = temp_index
                else:
                    temp_map[point] = index
                    self._data_3d.append(c2v(point))
                    self._index_map[(comp_index, point_index)] = index
                    index += 1
                point_index += 1
            comp_index += 1
        self._data_3d.append([0.0, 0, 1, 0])
        self._data_3d = np.array(self._data_3d)

    def _convert_3d_to_2d(self):
        def v2c(v):
            return complex(round(v[0], 1), round(v[1], 1))

        self._get_transformed_points()
        camera_transformed_points = Camera._camera_view(
            self._transformed_points)
        for comp_index, point_index in self._index_map:
            p = v2c(camera_transformed_points[self._index_map[(comp_index,
                                                               point_index)]])
            if point_index == 0:
                self._data_2d[comp_index].start = p
            if len(self._data_2d[comp_index]) == 2:
                if point_index == 1:
                    self._data_2d[comp_index].end = p
            else:
                if point_index == 1:
                    self._data_2d[comp_index].control1 = p
                elif point_index == 2:
                    self._data_2d[comp_index].control2 = p
                elif point_index == 3:
                    self._data_2d[comp_index].end = p

    def _apply_static_transform(self):
        def v2c(v):
            return complex(v[0], v[1])

        self._data_3d = self.static.dot(self._data_3d.T).T
        for comp_index, point_index in self._index_map:
            p = v2c(self._data_3d[self._index_map[(comp_index, point_index)]])
            if point_index == 0:
                self._data_2d[comp_index].start = p
            if len(self._data_2d[comp_index]) == 2:
                if point_index == 1:
                    self._data_2d[comp_index].end = p
            else:
                if point_index == 1:
                    self._data_2d[comp_index].control1 = p
                elif point_index == 2:
                    self._data_2d[comp_index].control2 = p
                elif point_index == 3:
                    self._data_2d[comp_index].end = p

        self._create_bbox()
        self.static = np.eye(4, dtype=np.float)
        return self

    # def _format_path_3d(self, data_3d):
    #     temp_map = dict()
    #     index = 0
    #     comp_index = 0
    #     identifier = 0
    #     for comp in data_3d:
    #         point_index = 0
    #         for point in comp[1:]:
    #             self._data_3d.append(point)

    #             if comp[0] == "l":
    #                 identifier = 11 if point_index == 0 else 12
    #             elif comp[0] == "p":
    #                 identifier = 21 if point_index == 0 else\
    #                              22 if point_index == 1 else\
    #                              23 if point_index == 2 else 24

    #             self._index_map[(identifier, comp_index, point_index)] = index
    #             point_index += 1
    #             index += 1
    #         comp_index += 1
    #     self._data_3d = np.array(self._data_3d)

    # def _c2v(self, z):
    #     return np.array([z.real, z.imag, 1])

    # def _v2c(self, v):
    #     return complex(v[0], v[1])

    # def abs_transform(self):
    #     matrix = self.transformation()
    #     if (matrix == np.eye(3)).all():
    #         return self
    #     for i in range(len(self)):
    #         self[i].start = self._v2c(matrix.dot(self._c2v(self[i].start)))
    #         self[i].end = self._v2c(matrix.dot(self._c2v(self[i].end)))
    #         if type(self[i]) == CubicBezier:
    #             self[i].control1 = self._v2c(
    #                 matrix.dot(self._c2v(self[i].control1)))
    #             self[i].control2 = self._v2c(
    #                 matrix.dot(self._c2v(self[i].control2)))
    #     self._create_bbox = matrix.dot(self._create_bbox.T).T
    #     self.dynamic_reset()
    #     self.reset()
    #     return self

    # def shift_index(self, index):
    #     for i in range(index - 1):
    #         self.append(self.pop(0))
    #     return self

    # def path2bezier(self, points_needed=None):
    #     for i in range(len(self.data)):
    #         start = self.data[i].start
    #         end = self.data[i].end
    #         if type(self.data[i]) == Line:
    #             self.data[i] = CubicBezier(start, start, end, end)
    #         elif type(self.data[i]) == QuadraticBezier:
    #             control = self.data[i].control
    #             self.data[i] = CubicBezier(start, (start + 2 * control) / 3,
    #                                        (2 * control + end) / 3, end)
    #     if points_needed:
    #         comp_len = []
    #         for i in range(len(self.data)):
    #             comp_len.append([i, self.data[i].length()])
    #         points_needed = points_needed - len(self.data)
    #         for i in range(points_needed):
    #             comp_len.sort(key=lambda x: x[0], reverse=True)
    #             index = comp_len[0][0]
    #             self.data[index:index + 1] = _split_bezier(self.data[index])
    #             _update_comp_len_list(comp_len, index)

    #     return self

    # def path2lines(self, points_needed):
    #     pts = []
    #     data = SVGPath()
    #     if points_needed > 0:
    #         for i in range(points_needed + 1):
    #             pts.append(self.data.point(i / points_needed))
    #         for start, end in zip(pts[:-1], pts[1:]):
    #             data.append(Line(start, end))
    #     state = self.__dict__.copy()
    #     state.pop("data", 0)
    #     return Path(data, **state)
