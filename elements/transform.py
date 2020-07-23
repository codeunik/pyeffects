import math

import numpy as np


class Transform:
    def __init__(self):
        self.dynamic = np.eye(4, dtype=np.float)
        self.static = np.eye(4, dtype=np.float)
        self.dynamic_to_static = dict()

    def transform_3d(self):
        return self.dynamic.dot(self.static)

    def transform_2d(self):
        transform_3d = self.transform_3d()
        a00 = transform_3d[0, 0]
        a01 = transform_3d[0, 1]
        a02 = transform_3d[0, 3]
        a10 = transform_3d[1, 0]
        a11 = transform_3d[1, 1]
        a12 = transform_3d[1, 3]
        return [a00, a10, a01, a11, a02, a12]

    def reset(self):
        self.static = np.eye(4, dtype=np.float)
        return self

    def translate(self, x=0, y=0, z=0):
        self.static = Transform.translation_matrix(x, y, z).dot(self.static)
        return self

    def scale(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        self.static = Transform.scale_matrix(sx, sy, sz, abs_anchor[:3]).dot(self.static)
        return self

    def rotate(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)
        self.static = Transform.rotation_matrix(angle, axis, abs_anchor[:3]).dot(self.static)
        return self

    def matrix(self, mat):
        self.static = mat.dot(self.static)
        return self

    def dynamic_reset(self):
        self.dynamic = np.eye(4, dtype=np.float)
        return self

    def dynamic_translate(self, x=0, y=0, z=0):
        self.dynamic = Transform.translation_matrix(x, y, z).dot(self.dynamic)
        return self

    def dynamic_scale(self, sx=1, sy=1, sz=1, anchor=[0.5, 0.5, 0.5]):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        self.dynamic = Transform.scale_matrix(sx, sy, sz, abs_anchor[:3]).dot(self.dynamic)
        return self

    def dynamic_rotate(self, angle=0, axis=[0, 0, 1], anchor=[0.5, 0.5, 0.5], abs=False):
        anchor = np.array([*anchor, 1])
        abs_anchor = self.anchor(self, anchor, abs)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)
        self.dynamic = Transform.rotation_matrix(angle, axis, abs_anchor[:3]).dot(self.dynamic)
        return self

    def dynamic_matrix(self, mat):
        self.dynamic = mat.dot(self.dynamic)
        return self

    def bbox(self):
        return self.transform_3d().dot(self._bbox.T).T

    def center(self):
        return self.bbox().sum(axis=0) / 2

    @staticmethod
    def translation_matrix(x, y, z):
        return np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1],
        ])

    @staticmethod
    def scale_matrix(sx, sy, sz, anchor):
        return Transform.translation_matrix(*anchor).dot(
            np.array([
                [sx, 0, 0, 0],
                [0, sy, 0, 0],
                [0, 0, sz, 0],
                [0, 0, 0, 1],
            ])).dot(Transform.translation_matrix(*-anchor))

    @staticmethod
    def rotation_matrix(angle, axis, anchor):
        rad_half_angle = math.radians(angle / 2)
        cos_half_angle = math.cos(rad_half_angle)
        sin_half_angle = math.sin(rad_half_angle)
        qx = axis[0] * sin_half_angle
        qy = axis[1] * sin_half_angle
        qz = axis[2] * sin_half_angle
        qw = cos_half_angle
        return Transform.translation_matrix(*anchor).dot(
            np.array([
                [1 - 2 * (qy**2 + qz**2), 2 * (qx * qy - qw * qz), 2 * (qx * qz + qw * qy), 0],
                [2 * (qx * qy + qw * qz), 1 - 2 * (qx**2 + qz**2), 2 * (qy * qz - qw * qx), 0],
                [2 * (qx * qz - qw * qy), 2 * (qy * qz + qw * qx), 1 - 2 * (qx**2 + qy**2), 0],
                [0, 0, 0, 1],
            ])).dot(Transform.translation_matrix(*-anchor))
