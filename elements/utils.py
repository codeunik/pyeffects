import numpy as np

class Color:
    @staticmethod
    def hex(color):
        if len(color) == 7:
            return np.array([int(color[i:i + 2], 16)/255.0 for i in (1, 3, 5)], dtype=np.int)
        else:
            return np.array([int(c * 2, 16)/255.0 for c in color[1:]], dtype=np.int)

    @staticmethod
    def rgb255(color):
        return np.array(color)/255.0

    @staticmethod
    def rgb1(color):
        return np.array(color)

    @staticmethod
    def to_hex(color):
        color *= 255
        rgb = color.astype(int)
        return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def unit_vector(v):
    v = np.array(v, dtype=np.float)
    v[:3] = v[:3] / np.linalg.norm(v[:3])
    return v


def four_vector(v):
    v = np.array(v)
    for i in range(len(v), 4):
        if i == 3:
            v = np.hstack((v, 1.0))
        else:
            v = np.hstack((v, 0.0))
    return v

