import numpy as np
import os
from .element import Element
import subprocess

class Image(Element):
    def __init__(self, x, y, width, height, img_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.filepath = os.path.abspath(img_path)
        Element.__init__(self)

    def set_dimension(self, x=None, y=None, width=None, height=None):
        self.x = x if x else self.x
        self.y = y if y else self.y
        self.width = width if width else self.width
        self.height = height if height else self.height

    def set_image(self, img_path):
        self.filepath = os.path.abspath(img_path)

    def _draw(self):
        attr_str = f'<image x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" href="{self.filepath}" transform="matrix(1 0 0 -1 0 1080) matrix{tuple(self.transform_2d())}" '
        attr_str += super()._draw()
        attr_str += "></image>"
        return attr_str

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


class Video(Image):
    def __init__(self, x, y, width, height, video_path):
        super(Video, self).__init__(x, y, width, height, video_path)

    def duration(self):
        return float(subprocess.check_output(
                f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {self.filepath}",
                shell=True))
        #ffmpeg -i mov.mp4 -r 60 -f image2 image-%07d.png

