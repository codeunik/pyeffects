import math

import numpy as np


class Transform:
    def __init__(self):
        self.dynamic = np.eye(3, dtype=np.float)
        self.static = np.eye(3, dtype=np.float)
        self.dynamic_to_static = dict()

    def get_transformation(self):
        #rhs_matrix = np.array([[1, 0, 0], [0, -1, 1080], [0, 0, 1.0]])
        #return rhs_matrix.dot(self.static)
        return self.transformation()

    def dynamic_reset(self):
        self.dynamic = np.eye(3, dtype=np.float)
        return self

    def reset(self):
        self.static = np.eye(3, dtype=np.float)
        return self

    def apply_matrix(self, mat):
        self.static = mat.dot(self.static)
        return self

    def transformation(self):
        return self.dynamic.dot(self.static)

    def translate(self, x=0, y=0):
        self.static = Transform.translation_matrix(x, y).dot(self.static)
        return self

    def scale(self, sx=1, sy=1, anchor_x=0.5, anchor_y=0.5, abs=False):
        anchor_x, anchor_y = self.anchor(self,
                                         anchor_x,
                                         anchor_y,
                                         abs_x=abs,
                                         abs_y=abs)
        self.static = Transform.scale_matrix(sx, sy, anchor_x,
                                             anchor_y).dot(self.static)
        return self

    def rotate(self, angle=0, anchor_x=0.5, anchor_y=0.5, abs=False):
        anchor_x, anchor_y = self.anchor(self,
                                         anchor_x,
                                         anchor_y,
                                         abs_x=abs,
                                         abs_y=abs)
        self.static = Transform.rotation_matrix(angle, anchor_x,
                                                anchor_y).dot(self.static)
        return self

    def skew_x(self, skew, anchor_x=0.0, anchor_y=0.0, abs=False):
        anchor_x, anchor_y = self.anchor(self,
                                         anchor_x,
                                         anchor_y,
                                         abs_x=abs,
                                         abs_y=abs)
        self.static = Transform.skew_x_matrix(skew, anchor_x,
                                              anchor_y).dot(self.static)
        return self

    def skew_y(self, skew, anchor_x=0.0, anchor_y=0.0, abs=False):
        anchor_x, anchor_y = self.anchor(self,
                                         anchor_x,
                                         anchor_y,
                                         abs_x=abs,
                                         abs_y=abs)
        self.static = Transform.skew_y_matrix(skew, anchor_x,
                                              anchor_y).dot(self.static)
        return self

    def dynamic_translate(self, x=0, y=0):
        self.dynamic = Transform.translation_matrix(x, y).dot(self.dynamic)
        return self

    def dynamic_scale(self, sx=1, sy=1, anchor_x=0.5, anchor_y=0.5):
        anchor_x, anchor_y = self.anchor(self, anchor_x, anchor_y)
        self.dynamic = Transform.scale_matrix(sx, sy, anchor_x,
                                              anchor_y).dot(self.dynamic)
        return self

    def dynamic_rotate(self, angle=0, anchor_x=0.5, anchor_y=0.5):
        anchor_x, anchor_y = self.anchor(self, anchor_x, anchor_y)
        self.dynamic = Transform.rotation_matrix(angle, anchor_x,
                                                 anchor_y).dot(self.dynamic)
        return self

    def dynamic_skew_x(self, skew, anchor_x=0.0, anchor_y=0.0):
        anchor_x, anchor_y = self.anchor(self, anchor_x, anchor_y)
        self.dynamic = Transform.skew_x_matrix(skew, anchor_x,
                                               anchor_y).dot(self.dynamic)
        return self

    def dynamic_skew_y(self, skew, anchor_x=0.0, anchor_y=0.0):
        anchor_x, anchor_y = self.anchor(self, anchor_x, anchor_y)
        self.dynamic = Transform.skew_y_matrix(skew, anchor_x,
                                               anchor_y).dot(self.dynamic)
        return self

    def bbox(self):
        cover = np.array([
            [self._bbox[0][0], self._bbox[0][1], 1.0],  # bottom_left_corner
            [self._bbox[1][0], self._bbox[0][1], 1.0],  # bottom_right_corner
            [self._bbox[0][0], self._bbox[1][1], 1.0],  # top_left_corner
            [self._bbox[1][0], self._bbox[1][1], 1.0]  # top_right_corner
        ])
        cover = self.transformation().dot(cover.T).T
        bottom_left_corner = cover[0]
        bottom_right_corner = cover[1]
        top_left_corner = cover[2]
        top_right_corner = cover[3]
        min_x = min(bottom_left_corner[0], bottom_right_corner[0],
                    top_left_corner[0], top_right_corner[0])
        max_x = max(bottom_left_corner[0], bottom_right_corner[0],
                    top_left_corner[0], top_right_corner[0])
        min_y = min(bottom_left_corner[1], bottom_right_corner[1],
                    top_left_corner[1], top_right_corner[1])
        max_y = max(bottom_left_corner[1], bottom_right_corner[1],
                    top_left_corner[1], top_right_corner[1])
        return np.array([[min_x, min_y], [max_x, max_y]])

    def center(self):
        return self.bbox().sum(axis=0) / 2

    @staticmethod
    def translation_matrix(x=0, y=0):
        return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])

    @staticmethod
    def scale_matrix(sx, sy, anchor_x, anchor_y):
        return np.array([[sx, 0, (1 - sx) * anchor_x],
                         [0, sy, (1 - sy) * anchor_y], [0, 0, 1]])

    @staticmethod
    def rotation_matrix(angle, anchor_x, anchor_y):
        c = math.cos((math.pi / 180) * angle)
        s = math.sin((math.pi / 180) * angle)
        return np.array([[c, -s, (1 - c) * anchor_x + s * anchor_y],
                         [s, c, (1 - c) * anchor_y - s * anchor_x], [0, 0, 1]])

    @staticmethod
    def skew_x_matrix(skew, anchor_x, anchor_y):
        skew = math.tan((math.pi / 180) * skew)
        return np.array([[1, skew, 0], [0, 1, 0], [-skew * anchor_y, 0, 1]])

    @staticmethod
    def skew_y_matrix(skew, anchor_x, anchor_y):
        skew = math.tan((math.pi / 180) * skew)
        return np.array([[1, 0, 0], [skew, 1, 0], [0, -skew * anchor_x, 1]])
