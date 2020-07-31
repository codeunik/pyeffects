from .utils import Color


class Def:
    pass


class Gourad(Def):
    pass


#     <svg xmlns="http://www.w3.org/2000/svg" version="1.200000" width="100%" height="100%" viewBox="0 0 100.000000 86.600000" xmlns:xlink="http://www.w3.org/1999/xlink">
#   <g transform="matrix(1 0 0 -1 0 86.600000)">
#     <defs>

#       <linearGradient id="fadeA-1" gradientUnits="userSpaceOnUse" x1="50.000000" y1="0.000000" x2="50.000000" y2="86.600000">
#         <stop offset="0%" stop-color="#FF0000"/>
#         <stop offset="100%" stop-color="#000000" />
#       </linearGradient>
#       <linearGradient id="fadeB-1" gradientUnits="userSpaceOnUse" x1="0.000000" y1="86.60000" x2="75.000000" y2="43.300000">
#         <stop offset="0%" stop-color="#00FF00"/>
#         <stop offset="100%" stop-color="#000000" />
#       </linearGradient>
#       <linearGradient id="fadeC-1" gradientUnits="userSpaceOnUse" x1="100.000000" y1="86.60000" x2="25.000000" y2="43.300000">
#         <stop offset="0%" stop-color="#0000FF"/>
#         <stop offset="100%" stop-color="#000000" />
#       </linearGradient>

#       <path id="pathA-1" d="M 50.000000,0.000000 L 0.000000,86.600000 100.000000,86.600000 Z" fill="url(#fadeA-1)"/>
#       <path id="pathB-1" d="M 50.000000,0.000000 L 0.000000,86.600000 100.000000,86.600000 Z" fill="url(#fadeB-1)"/>
#       <filter id="Default">
#         <feImage xlink:href="#pathA-1" result="layerA" x="0" y="0" />
#         <feImage xlink:href="#pathB-1" result="layerB" x="0" y="0" />
#         <feComposite in="layerA" in2="layerB" operator="arithmetic" k1="0" k2="1.0" k3="1.0" k4="0" result="temp"/>
#         <feComposite in="temp" in2="SourceGraphic"   operator="arithmetic" k1="0" k2="1.0" k3="1.0" k4="0"/>
#       </filter>
#     </defs>
#     <g stroke="none" stroke-width="0"shape-rendering=" crispEdges" >
#       <path d="M 50.000000,0.000000 L 0.000000,86.600000 100.000000,86.600000 Z" fill="url(#fadeC-1)" filter="url(#Default)" />
#     </g>
#   </g>
# </svg>


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
