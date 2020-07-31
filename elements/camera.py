import math

import numpy as np

from .light import Light
from .transform import Transform
from .utils import unit_vector


class Camera:
    _aspect_ratio = 9 / 16
    _position = np.array([960, 540, 960, 1])
    _focus = unit_vector([0.0, 0, -1, 1])
    _up = unit_vector([0.0, 1, 0, 1])
    _is_perspective = True

    def set_camera_from_viewport(top, bottom, left, right):
        pos_x = (left + right) / 2
        pos_y = (top + bottom) / 2
        pos_z = (right - left) / 2
        Camera._position = np.array([pos_x, pos_y, pos_z, 1.0])
        Camera._focus = unit_vector([0.0, 0, -1, 1])
        Camera._up = unit_vector([0.0, 1, 0, 1])
        Camera._aspect_ratio = (top - bottom) / (right - left)
        return Camera

    def set_position(position):
        Camera._position = position
        return Camera

    def get_position():
        return Camera._position

    def set_up_direction(up):
        Camera._up = up
        return Camera

    def get_up_direction():
        return Camera._up

    def set_focus(focus):
        Camera._focus = unit_vector(focus)
        return Camera

    def get_focus():
        return Camera._focus

    def _camera_transform():
        zero = np.array([0.0, 0, 0])
        y = np.array([0.0, 1, 0])
        n = np.cross(Camera._up[:3], y)
        up_angle = math.acos(np.dot(Camera._up[:3], y))
        focus_angle = math.acos(
            np.dot(Camera._focus[:3], np.array([0.0, 0, -1])))
        return Transform.rotation_matrix(focus_angle, y, zero).dot(
            Transform.rotation_matrix(up_angle, n, zero)).dot(
                Transform.translation_matrix(*(np.array([0.0, 0, 1]) -
                                               Camera._position[:3])))

    def _camera_view(points):
        camera_transformed_points = Camera._camera_transform().dot(points.T).T
        if camera_transformed_points[:, 2].min() > 0:
            return np.zeros(camera_transformed_points.shape)
        if Camera._is_perspective:
            np.apply_along_axis(Camera._perspective_transform, 1,
                                camera_transformed_points)
        return camera_transformed_points

    def _perspective_transform(point):
        point[0] = ((point[0] / (1 - point[2])) + 1) * 960
        point[1] = ((point[1] / (1 - point[2])) + Camera._aspect_ratio) * 960
