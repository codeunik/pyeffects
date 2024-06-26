import numpy as np
import os
from .element import Element
import subprocess
import base64
from PIL import ImageOps, Image as PILImage
from io import BytesIO

class TSpan(Element):
    def __init__(self, text):
        self.text = text
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1

        Element.__init__(self)
    
    def _draw(self):
        attr_str = '<tspan '
        attr_str += super()._draw()
        attr_str += f">{self.text}</tspan>"
        return attr_str

    def bbox(self):
        a00, a10, a01, a11, a02, a12 = self.transform_2d()
        matrix = np.array([[a00, a01, a02], [a10, a11, a12], [0, 0, 1]])
        vertices = np.array([
            [self.x, self.y, 1],
            [self.x + self.width, self.y, 1],
            [self.x + self.width, self.y + self.height, 1],
            [self.x, self.y + self.height, 1],
        ])
        transformed_vertices = matrix.dot(vertices.T).T
        return np.array([[transformed_vertices[:,0].min(), transformed_vertices[:,1].min(), 1.0, 1.0],
                         [transformed_vertices[:,0].max(), transformed_vertices[:,1].max(), 1.0, 1.0]])



class Text(Element):
    def __init__(self, text, x, y, font_size=None, font_family=None, text_anchor='middle'):
        self.text = text if type(text) == list else [text]
        self.text = [TSpan(t) for t in self.text]
        self.x = x
        self.y = y
        self.width = 1
        self.height = 1

        self.style = {
            'font-size': font_size,
            'font-family': font_family,
            'text-anchor': text_anchor, # start, middle, end
        }
        Element.__init__(self)

    def _draw(self):
        attr_str = f'<text x="{self.x}" y="{1080-self.y}"' \
                   f' transform="matrix(1, 0, 0, -1, 0, 1080)" '\
                   ' style="{}" '.format(";".join(f'{k}: {v}' for k, v in self.style.items() if v is not None))
        attr_str += super()._draw()
        attr_str += f">{' '.join([t._draw() for t in self.text])}</text>"
        return attr_str

    def border_length(self):
        a00, a10, a01, a11, a02, a12 = self.transform_2d()
        matrix = np.array([[a00, a01, a02], [a10, a11, a12], [0, 0, 1]])
        vertices = np.array([
            [self.x, self.y, 1],
            [self.x + self.width, self.y, 1],
            [self.x + self.width, self.y + self.height, 1],
            [self.x, self.y + self.height, 1],
        ])
        transformed_vertices = matrix.dot(vertices.T).T
        return np.linalg.norm(transformed_vertices[1] - transformed_vertices[0])\
            + np.linalg.norm(transformed_vertices[2] - transformed_vertices[1])\
            + np.linalg.norm(transformed_vertices[3] - transformed_vertices[2])\
            + np.linalg.norm(transformed_vertices[0] - transformed_vertices[3])

    def bbox(self):
        a00, a10, a01, a11, a02, a12 = self.transform_2d()
        matrix = np.array([[a00, a01, a02], [a10, a11, a12], [0, 0, 1]])
        vertices = np.array([
            [self.x, self.y, 1],
            [self.x + self.width, self.y, 1],
            [self.x + self.width, self.y + self.height, 1],
            [self.x, self.y + self.height, 1],
        ])
        transformed_vertices = matrix.dot(vertices.T).T
        return np.array([[transformed_vertices[:,0].min(), transformed_vertices[:,1].min(), 1.0, 1.0],
                         [transformed_vertices[:,0].max(), transformed_vertices[:,1].max(), 1.0, 1.0]])

