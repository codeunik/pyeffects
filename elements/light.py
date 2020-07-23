import numpy as np


class Light:
    _position = np.array([960, 540, 300.0, 1])
    _color = np.array([255, 255, 255])

    def set_position(position):
        Light._position = position

    def set_color(color):
        Light._color = color

    def get_color():
        return Light._color

    def get_position():
        return Light._position
