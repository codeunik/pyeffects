import numpy as np
import os
from .element import Element
from .path import Path
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
        attr_str = '<span style="'
        attr_str += super()._draw().replace("fill", "-webkit-text-fill-color")\
            .replace("stroke", "-webkit-text-stroke-color")\
            .replace("stroke-width", "-webkit-text-stroke-width")\
            .replace('="', ":").replace('"', ";") + '"'
        attr_str += f'>{self.text}</span>'
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



class TextBox(Element):
    def __init__(self, text, x, y, width, height, font_size=None, font_family=None, text_align="center", align_items='center', justify_content='center'):
        self.text = text if type(text) == list else [text]
        self.text = [TSpan(t) for t in self.text]
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.style = {
            'font-size': font_size,
            'font-family': font_family,
            'text-align': text_align
        }
        self.align_items = align_items
        self.justify_content = justify_content
        Element.__init__(self)
    def _draw(self):
        attr_str = f'<foreignObject x="{self._x}" y="{1080-self._y-self.height}" width="{self._width}" height="{self._height}"' \
                   f' transform="matrix(1, 0, 0, -1, 0, 1080)" '\
                   ' style="{}; '.format(";".join(f'{k}: {v}' for k, v in self.style.items() if v is not None))
        attr_str += super()._draw().replace("fill", "-webkit-text-fill-color")\
            .replace("stroke=", "-webkit-text-stroke-color=")\
            .replace("stroke-width=", "-webkit-text-stroke-width=")\
            .replace('="', ":").replace('"', ";") + '"'
        attr_str += f"""><body xmlns="http://www.w3.org/1999/xhtml" style="height: -webkit-fill-available; align-items: {self.align_items}; display: flex; justify-content: {self.justify_content};"><div>{' '.join([t._draw() for t in self.text])}</div></body></foreignObject>"""
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
        self._x = transformed_vertices[:,0].min()
        self._y = transformed_vertices[:,1].min()
        self._width = transformed_vertices[:,0].max() - self._x
        self._height = transformed_vertices[:,1].max() - self._y
        return np.array([[transformed_vertices[:,0].min(), transformed_vertices[:,1].min(), 1.0, 1.0],
                         [transformed_vertices[:,0].max(), transformed_vertices[:,1].max(), 1.0, 1.0]])

