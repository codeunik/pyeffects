from .utils import Color


class Def:
    pass


class LinearGradient(Def):
    count = 0

    def __init__(self):
        self.id = f"lg{LinearGradient.count}"
        LinearGradient.count += 1
        self.x1 = 0
        self.y1 = 0
        self.x2 = 1
        self.y2 = 1
        self.gradients = []

    def spread(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        return self

    def add_gradient(self, offset, stop_color, opacity=1):
        if isinstance(stop_color, list):
            stop_color = Color.rgb(stop_color)
        self.gradients.append([offset, stop_color, opacity])
        return self

    def _str_def(self):
        s = f'<linearGradient id="{self.id}" x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}">'
        for gradient in self.gradients:
            s += f'<stop offset="{gradient[0]*100}%" stop-color="{Color.to_hex(gradient[1])}" stop-opacity="{gradient[2]}"/>'
        s += "</linearGradient>"
        return s


class RadialGradient(Def):
    count = 0

    def __init__(self):
        self.id = f"rg{RadialGradient.count}"
        RadialGradient.count += 1
        self.cx = 0.5
        self.cy = 0.5
        self.r = 0.5
        self.fx = 0.5
        self.fy = 0.5
        self.gradients = []

    def spread(self, cx, cy, r):
        self.cx = cx
        self.cy = cy
        self.r = r
        return self

    def focus(self, fx, fy):
        self.fx = fx
        self.fy = fy
        return self

    def add_gradient(self, offset, stop_color, opacity=1):
        if isinstance(stop_color, list):
            stop_color = Color.rgb(stop_color)
        self.gradients.append([offset, stop_color, opacity])
        return self

    def _str_def(self):
        s = f'<radialGradient id="{self.id}" cx="{self.cx}" cy="{self.cy}" r="{self.r}" fx="{self.fx}" fy="{self.fy}">'
        for gradient in self.gradients:
            s += f'<stop offset="{gradient[0]*100}%" stop-color="{Color.to_hex(gradient[1])}" stop-opacity="{gradient[2]}"/>'
        s += "</radialGradient>"
        return s


class ClipPath(Def):
    count = 0

    def __init__(self, element):
        self.id = f"cp{ClipPath.count}"
        ClipPath.count += 1
        self.element = element

    def _str_def(self):
        return f'<mask id="{self.id}">{self.element.draw()}</mask>'


class Mask(Def):
    count = 0

    def __init__(self, element):
        self.id = f"m{Mask.count}"
        Mask.count += 1
        self.element = element

    def _str_def(self):
        return f'<clipPath id="{self.id}">{self.element.draw()}</clipPath>'
