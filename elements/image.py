import numpy as np

from .element import Element


class Image(Element):
    def __init__(self, x, y, width, height, img_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img_path = img_path
        Element.__init__(self)

    def set_dimension(self, x=None, y=None, width=None, height=None):
        self.x = x if x else self.x
        self.y = y if y else self.y
        self.width = width if width else self.width
        self.height = height if height else self.height

    def set_image(self, img_path):
        self.img_path = img_path

    def _draw(self):
        attr_str = f'<image x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" href="{self.img_path}" transform="{tuple(self.transform_2d())}"'
        attr_str += super()._draw()
        attr_str += "></image>"
        return s

    def _border_length(self):
        a00, a10, a01, a11, a02, a12 = self.transform_2d()
        matrix = np.array([[a00, a01, a02], [a10, a11, a12], [0, 0, 1]])
        vertices = np.array([
            [self.x, self.y, 1],
            [self.x + self.width, self.y, 1],
            [self.x + self.width, self.y + self.height, 1],
            [self.x, self.y + self.height, 1],
        ])
        transformed_vertices = matrix.dot(vertices.T).T
        return np.linalg.norm(vertices[1] - vertices[0])\
            + np.linalg.norm(vertices[2] - vertices[1])\
            + np.linalg.norm(vertices[3] - vertices[2])\
            + np.linalg.norm(vertices[0] - vertices[3])

    #TODO
    def bbox(self):
        pass
