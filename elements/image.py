import numpy as np
import os
from .element import Element
import subprocess
import base64
from PIL import ImageOps, Image as PILImage
from io import BytesIO



class Image(Element):
    def __init__(self, x, y, width, height, img_path, preserve_aspect_ratio="xMidYMid slice"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        img = PILImage.open(os.path.abspath(img_path))
        img_flip = ImageOps.flip(img)
        buffered = BytesIO()
        img_flip.save(buffered, format="PNG")
        self.base64_encode = base64.b64encode(buffered.getvalue()).decode('utf-8')
        self.preserve_aspect_ratio = preserve_aspect_ratio
        Element.__init__(self)

    def set_dimension(self, x=None, y=None, width=None, height=None):
        self.x = x if x else self.x
        self.y = y if y else self.y
        self.width = width if width else self.width
        self.height = height if height else self.height

    def set_image(self, img_path):
        self.filepath = os.path.abspath(img_path)

    def _draw(self):
        attr_str = f'<image x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" xlink:href="data:image/png;base64,{self.base64_encode}"' \
                   f' transform="matrix{tuple(self.transform_2d())}" preserveAspectRatio="{self.preserve_aspect_ratio}" '
        attr_str += super()._draw()
        attr_str += "></image>"
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


class Video(Image):
    def __init__(self, x, y, width, height, video_path, preserve_aspect_ratio="xMidYMid slice"):
        super(Video, self).__init__(x, y, width, height, video_path, preserve_aspect_ratio)

    def duration(self):
        return float(subprocess.check_output(
                f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {self.filepath}",
                shell=True))
        #ffmpeg -i mov.mp4 -r 60 -f image2 image-%07d.png

