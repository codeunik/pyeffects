from copy import deepcopy

import bs4
import numpy as np

from .path import Path
from .shapes import *


class SVGParser:
    def __init__(self, svg_file):
        with open(svg_file, "r") as f:
            self.soup = bs4.BeautifulSoup(f.read(), 'lxml-xml')
        self.data = dict()
        self.parse(self.soup.svg, {"transform": list()}, self.data)
        self.create_elements(self.data)

    def parse(self, parent_tag, inherited_attrs, layer):
        for tag in parent_tag.children:
            if tag.name is None:
                pass
            else:
                attrs = deepcopy(inherited_attrs)
                tag_attrs = tag.attrs
                temp = tag_attrs.pop("transform") if tag_attrs.get(
                    "transform", False) else None
                attrs.update(tag_attrs)
                attrs["transform"].insert(0, temp) \
                    if temp is not None else None
                if tag.name == "g":
                    layer[tag["id"]] = dict()
                    self.parse(tag, attrs, layer[tag["id"]])
                else:
                    attrs.update({"name": tag.name})
                    layer[tag["id"]] = attrs

    def create_elements(self, groups):
        for item in groups:
            if not groups[item].get("name", False):
                self.create_elements(groups[item])
            else:
                element_attrs = groups[item]
                if element_attrs["name"] == "path":
                    element = Path(element_attrs["d"])
                elif element_attrs["name"] == "rect":
                    x = float(element_attrs["x"])
                    y = float(element_attrs["y"])
                    width = float(element_attrs["width"])
                    height = float(element_attrs["height"])
                    rx = float(element_attrs.get("rx", 0))
                    ry = float(element_attrs.get("ry", 0))
                    element = Rectangle(x, y, width, height, rx, ry)
                elif element_attrs["name"] == "circle":
                    cx = float(element_attrs["cx"])
                    cy = float(element_attrs["cy"])
                    r = float(element_attrs["r"])
                    element = Circle(cx, cy, r)
                elif element_attrs["name"] == "ellipse":
                    cx = float(element_attrs["cx"])
                    cy = float(element_attrs["cy"])
                    rx = float(element_attrs["rx"])
                    ry = float(element_attrs["ry"])
                    element = Ellipse(cx, cy, rx, ry)
                elif element_attrs["name"] == "line":
                    x1 = float(element_attrs["x1"])
                    y1 = float(element_attrs["y1"])
                    x2 = float(element_attrs["x2"])
                    y2 = float(element_attrs["y2"])
                    element = Line(x1, y1, x2, y2)
                elif element_attrs["name"] == "polyline":
                    d = element_attrs["points"]
                    pos = d.index(" ", d.index(" ") + 1)
                    d = "M" + d[:pos + 1] + "L" + d[pos + 1:]
                    element = Path(d)
                elif element_attrs["name"] == "polyon":
                    d = element_attrs["points"]
                    pos = d.index(" ", d.index(" ") + 1)
                    d = "M" + d[:pos + 1] + "L" + d[pos + 1:] + "z"
                    element = Path(d)

                element.stroke(element_attrs["stroke"]) \
                    if element_attrs.get("stroke", False) else None

                element.stroke_width(float(element_attrs["stroke-width"])) \
                    if element_attrs.get("stroke-width", False) else None

                element.fill(element_attrs["fill"]) \
                    if element_attrs.get("fill", False) else None

                element.opacity(float(element_attrs["opacity"])) \
                    if element_attrs.get("opacity", False) else None

                element.fill_opacity(float(element_attrs["fill-opacity"])) \
                    if element_attrs.get("fill-opacity", False) else None

                element.stroke_opacity(float(element_attrs["stroke-opacity"])) \
                    if element_attrs.get("stroke-opacity", False) else None

                element.stroke_linecap(element_attrs["stroke-linecap"]) \
                    if element_attrs.get("stroke-linecap", False) else None

                element.stroke_linejoin(float(element_attrs["stroke-linejoin"])) \
                    if element_attrs.get("stroke-linejoin", False) else None

                element.stroke_miterlimit(float(element_attrs["stroke-miterlimit"])) \
                    if element_attrs.get("stroke-miterlimit", False) else None

                element.stroke_dashoffset(float(element_attrs["stroke-dashoffset"])) \
                    if element_attrs.get("stroke-dashoffset", False) else None

                element.fill_rule(float(element_attrs["fill-rule"])) \
                    if element_attrs.get("fill-rule", False) else None

                if element_attrs.get("stroke-dasharray", False):
                    d = dict()
                    exec("x=(" + element_attrs["stroke-dasharray"] + ")", d)
                    element.stroke_dasharray(d['x'])

                self.apply_transforms(element, element_attrs["transform"]) \
                    if element_attrs.get("transform", False) else None

                groups[item] = element

    def element_tree(self):
        return self.data

    def apply_transforms(self, element, transforms):
        d = dict()
        for transform in transforms:
            if "translate" in transform:
                exec(transform.replace("translate", "x=").replace(" ", ","), d)
                element.translate(*d['x'])
            elif "scale" in transform:
                exec(transform.replace("scale", "x=").replace(" ", ","), d)
                if type(d['x']) == tuple:
                    element.scale(d['x'][0], d['x'][1], 0, 0, True)
                else:
                    element.scale(d['x'], d['x'], 0, 0, True)
            elif "rotate" in transform:
                exec(transform.replace("rotate", "x=").replace(" ", ","), d)
                if type(d['x']) == tuple:
                    element.rotate(d['x'][0], d['x'][1], d['x'][2], True)
                else:
                    element.rotate(d['x'], 0, 0, True)
            elif "skewX" in transform:
                exec(transform.replace("skewX", "x=").replace(" ", ","), d)
                element.skew_x(*d['x'])
            elif "skewY" in transform:
                exec(transform.replace("skewY", "x=").replace(" ", ","), d)
                element.skew_y(*d['x'])
            else:
                exec(transform.replace("matrix", "x=").replace(" ", ","), d)
                element.apply_matrix(
                    np.array([[d['x'][0], d['x'][2], d['x'][4]],\
                              [d['x'][1], d['x'][3], d['x'][5]],\
                              [0, 0, 1.0]]))
        element.apply_matrix(np.array([[1, 0, 0], [0, -1, 1080], [0, 0, 1]]))
