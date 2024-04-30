import numpy as np

class FrameConfig:
    width = 1920
    height = 1080

class Color:
    def __init__(self, hsv=None, rgb=None, hex=None):
        # in the range (0,0,0) - (1,1,1)
        if hsv is not None:
            self.specification = 'hsv'
            self.value = np.array(hsv)
        elif rgb is not None:
            self.specification = 'rgb'
            self.value = np.array(rgb)
        elif hex is not None:
            self.specification = 'rgb'
            self.value = np.array(tuple(int(hex[i:i+2], 16)  for i in (0, 2, 4)))

    # @staticmethod
    # def hex(color):
    #     if len(color) == 7:
    #         return np.array([int(color[i:i + 2], 16)/255.0 for i in (1, 3, 5)], dtype=int)
    #     else:
    #         return np.array([int(c * 2, 16)/255.0 for c in color[1:]], dtype=int)

    # @staticmethod
    # def to_hex(color):
    #     color *= 255
    #     rgb = color.astype(int)
    #     return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def unit_vector(v):
    v = np.array(v, dtype=float)
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

