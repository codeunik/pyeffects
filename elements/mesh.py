import numpy as np

from .camera import Camera
from .defs import LinearGradient
from .group import Group
from .light import Light
from .path import Path
from .utils import four_vector, unit_vector


class FourVectors:
    def __init__(self):
        self.vectors = np.array([0, 0, 0, 0.0])

    def add_vector(self, vertex):
        self.vectors = np.vstack((self.vectors, vertex))

    def get_transformed_points(self, transformation):
        return transformation.dot(self.vectors.T).T


class Mesh:
    def __init__(self, is_transparent=False):
        self.vertices = np.array([0.0, 0, 0, 0])
        self.vertex_normals = np.array([0.0, 0, 0, 0])
        self.faces = []
        self._is_transparent = is_transparent

    def add_vertex(self, vertex):
        self.vertices = np.vstack((self.vertices, vertex))

    def add_vertex_normal(self, vertex):
        self.vertices = np.vstack((self.vertices, vertex))

    def add_face(self, face):
        self.faces.append(face)

    def fill_opacity(self, val):
        if val != 1:
            for face in self:
                face._is_transparent = True
        return super().fill_opacity(val)

    def opacity(self, val):
        if val != 1:
            for face in self:
                face._is_transparent = True
        return super().opacity(val)


class Face(Path):
    def __init__(self, vertices, is_transparent=False):
        self._vertices = vertices
        self._vertex_normals = None
        self._is_transparent = is_transparent

        self._color = np.array([255, 255, 255])
        self._ambient = np.array([0.2, 0.2, 0.2])
        self._diffuse = np.array([0.5, 0.5, 0.6])
        self._specular = np.array([0.2, 0.25, 0.3])
        self._specular_k = 50

        super().__init__(None)
        if self._vertices:
            self.create_face()

    def add_vertex(self, vertex):
        self._vertices.append(vertex)

    def done(self):
        if self._vertices:
            self.create_face()
        return self

    def add_vertex_normal(self, vertex_normal):
        self._vertex_normals.append(unit_vector(vertex_normal))

    def set_color(self, color, ambient, diffuse, specular):
        self._color = color
        self._ambient = ambient
        self._diffuse = diffuse
        self._specular = specular

    def create_face(self):
        n = len(self._vertices)
        segs = []
        for i in range(n - 1):
            segs.append(['l', self._vertices[i], self._vertices[i + 1]])
        segs.append(['l', self._vertices[n - 1], self._vertices[0]])
        self.set_segments(segs, True)

    def add_path_face(self, data):
        self.set_segments(data, True)

    def is_hidden_surface(self):
        v0 = self._transformed_vertices[0]
        v1 = self._transformed_vertices[1]
        v2 = self._transformed_vertices[2]
        self._face_normal = unit_vector(four_vector(np.cross((v1 - v0)[:3], (v2 - v0)[:3])))

        if not self._is_transparent:
            if self._face_normal.dot(unit_vector(Camera.get_position() - v0)) <= 0:
                return True
        return False

    def convert_3d_to_2d(self):
        if self._is_transparent:
            self.fill(self._color)
            self.stroke(self._color)
        else:
            if self._vertex_normals:
                face_gradient = self.get_face_gradient()
                self.fill(face_gradient)
                self.stroke(face_gradient)

            else:
                v0 = self._transformed_vertices[0]
                v1 = self._transformed_vertices[1]
                v2 = self._transformed_vertices[2]
                self._face_normal = unit_vector(four_vector(np.cross((v1 - v0)[:3], (v2 - v0)[:3])))
                face_color = self.get_light_value(self._face_vertices_avg, self._face_normal)
                self.fill(face_color)
                self.stroke(face_color)

        super().convert_3d_to_2d()

    def get_z_index(self):
        self._vertices = np.array(self._vertices)
        self._transformed_vertices = self.transform_3d().dot(self._vertices.T).T
        self._face_vertices_avg = sum(self._transformed_vertices) / len(self._transformed_vertices)
        self.z_index(self._face_vertices_avg[2])
        return self._z_index

    def get_light_value(self, face_point, normal):
        face_to_light = unit_vector(Light.get_position() - face_point)
        half_vector = unit_vector(face_to_light + Camera.get_position() - face_point)
        diffuse_coeff = self._diffuse * (normal[:3].dot(face_to_light[:3]))
        specular_coeff = self._specular * (normal.dot(half_vector))**self._specular_k
        face_color = (self._color * (self._ambient + diffuse_coeff) +
                      Light.get_color() * specular_coeff).astype(np.int)
        return face_color

    # def draw(self):
    #     is_hidden_face = self.is_hidden_surface()
    #     if is_hidden_face:
    #         return ""
    #     else:
    #         return super().draw()

    def get_face_gradient(self):
        def get_gradient_spread(vertices, i1, i2):
            vertices = Camera.world_view(vertices, np.eye(4))
            min_x = vertices[:, 0].min()
            min_y = vertices[:, 1].min()
            max_x = vertices[:, 0].max()
            max_y = vertices[:, 1].max()
            width = max_x - min_x
            height = max_y - min_y
            v1 = vertices[i1]
            v2 = vertices[i2]
            return [(v1[0] - min_x) / width, (v1[1] - min_y) / height, (v2[0] - min_x) / width,
                    (v2[1] - min_y) / height]

        vertex_normals = np.array(self._vertex_normals)
        vertex_normals = self.transform_3d().dot(vertex_normals.T).T
        vertex_colors = sorted([[
            i,
            self.get_light_value(self._transformed_vertices[i], unit_vector(vertex_normals[i]))
        ] for i in range(len(self._transformed_vertices))],
                               key=lambda x: np.linalg.norm(x[1]))
        light_shade = vertex_colors[0][1]
        dark_shade = vertex_colors[-1][1]

        lg = LinearGradient().spread(*get_gradient_spread(
            self._transformed_vertices, vertex_colors[0][0], vertex_colors[-1][0])).add_gradient(
                0, light_shade).add_gradient(1, dark_shade)
        return lg
        # print(self._vertices)
        # print(self._transformed_vertices)
        # print(vertex_normals)
        # print(vertex_colors)
        # print(light_shade)
        # print(dark_shade)
        # print(
        #     get_gradient_spread(self._transformed_vertices, vertex_colors[0][0],
        #                         vertex_colors[-1][0]))
        # print("-----------------------------")


def parse_obj_file(obj_file):
    with open(obj_file, "r") as f:
        mesh_desc = f.readlines()

    mesh = Mesh()
    vertices = [None]
    vertex_normals = [None]
    for line in mesh_desc:
        if line[:2] == "v ":
            vertices.append(
                four_vector(
                    [float(x) for x in list(filter(lambda a: a != "", line[2:].split(" ")))]))
        elif line[:3] == "vn ":
            vertex_normals.append(
                four_vector(
                    unit_vector(
                        [float(x) for x in list(filter(lambda a: a != "", line[3:].split(" ")))])))
        elif line[:2] == "f ":
            face = Face()
            if "/" in line:
                for vertex_desc in list(filter(lambda a: "/" in a, line[2:].split(" "))):
                    vertex_index, _, normal_index = vertex_desc.split("/")
                    vertex_index = int(vertex_index)
                    normal_index = int(normal_index)
                    face.add_vertex(vertices[vertex_index])
                    face.add_vertex_normal(vertex_normals[normal_index])
            else:
                for vertex_index in list(filter(lambda a: a != "", line[2:].split(" "))):
                    vertex_index = int(vertex_index)
                    face.add_vertex(vertices[vertex_index])
            face.done()
            mesh.add_face(face)
    return mesh.scale(200, 200, 200).translate(860, 440, -300)
