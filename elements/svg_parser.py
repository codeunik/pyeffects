import math
import re
from copy import deepcopy

import bs4
import numpy as np

from .path import Path
from .shapes import *
import uuid
import pandas as pd
from .defs import Mask, ClipPath, Group
 
class SVGParser:
    def __init__(self, svg_file):
        with open(svg_file, "r") as f:
            self.soup = bs4.BeautifulSoup(f.read(), 'lxml-xml')
        self.element_tree = dict()
        self._parse(self.soup.svg, {"transform": list()}, self.element_tree)
        self._create_elements(self.element_tree)
        self.defs = self.element_tree.pop('defs')
        self._flatten_tree = pd.json_normalize(self.element_tree, sep='.').to_dict(orient='records')[0]

    def element_by_selectors(self, *selectors):
        elements = []
        for k in self._flatten_tree:
            flag = 0
            for selector in selectors:
                if selector in k:
                    flag += 1
            if flag == len(selectors):
                elements.append(self._flatten_tree[k])
        return Group(*elements)

    def _parse(self, parent_tag, inherited_attrs, layer):
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
                
                if attrs.get("style", False):
                    element_styles = attrs['style'].replace(' ', '')
                    element_styles = element_styles.split(';')
                    for style in element_styles:
                        k, v = style.split(':')
                        if v == 'none':
                            v = None
                        attrs[k] = v

                if tag.name == "g":
                    tag_id = tag.get("id", str(uuid.uuid4().hex))
                    layer[tag_id] = dict()
                    self._parse(tag, attrs, layer[tag_id])
                elif tag.name == 'defs':
                    attrs.update({"name": tag.name})
                    layer["defs"] = dict()
                    self._parse(tag, attrs, layer["defs"])
                elif tag.name == 'clipPath' or tag.name == 'mask' or tag.name == 'linearGradient' or tag.name == 'radialGradient':
                    attrs.update({"name": tag.name})
                    layer[tag["id"]] = dict()
                    self._parse(tag, attrs, layer[tag["id"]])
                else:
                    attrs.update({"name": tag.name})
                    layer[tag.get("id", str(uuid.uuid4().hex))] = attrs

    def _create_elements(self, groups):
        for item in groups:
            if not groups[item].get("name", False):
                self._create_elements(groups[item])
            else:
                element_attrs = groups[item]
                element = None
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

                self._apply_transforms(element, element_attrs["transform"]) \
                    if element_attrs.get("transform", False) else None
                if element:
                    element = element.matrix(
                            np.array([
                                [1, 0, 0, 0],
                                [0, -1, 0, 1080],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1],
                            ]))

                # if element_attrs.get('clip-path', False):
                #     clip_paths = []
                #     for x in self.element_tree['defs'][element_attrs["clip-path"][5:-1]]:
                #         x = self.element_tree['defs'][element_attrs["clip-path"][5:-1]][x]
                #         if isinstance(x, Path):
                #             clip_paths.append(x)
                #     element.clip_path(ClipPath(Group(*clip_paths).matrix(element.static)))
                
                if element_attrs.get('mask', False):
                    mask = []
                    for x in self.element_tree['defs'][element_attrs["mask"][5:-1]]:
                        x = self.element_tree['defs'][element_attrs["mask"][5:-1]][x]
                        if isinstance(x, Path):
                            mask.append(x)
                    element.mask(Mask(Group(*mask).matrix(element.static)))

                element.stroke(element_attrs["stroke"]) if element_attrs.get("stroke", False) else None

                element.stroke_width(float(re.findall('\d*\.?\d+',element_attrs["stroke-width"])[0])) \
                    if element_attrs.get("stroke-width", False) else None

                if element_attrs.get('fill', False):
                    if 'url' in element_attrs['fill']:
                        for x in self.element_tree['defs'][element_attrs["fill"][5:-1]]:
                            x = self.element_tree['defs'][element_attrs["fill"][5:-1]][x]
                            if type(x) == dict:
                                if x.get('stop-color', False):
                                    #TODO: get the average of stop-colors
                                    element.fill(x['stop-color'])
                    else:
                        element.fill(element_attrs["fill"])
                elif isinstance(element, Path):
                    element.fill("white")

                element.opacity(float(element_attrs["opacity"])) \
                    if element_attrs.get("opacity", False) else None

                element.fill_opacity(float(element_attrs["fill-opacity"])) \
                    if element_attrs.get("fill-opacity", False) else None

                element.stroke_opacity(float(element_attrs["stroke-opacity"])) \
                    if element_attrs.get("stroke-opacity", False) else None

                element.stroke_linecap(element_attrs["stroke-linecap"]) \
                    if element_attrs.get("stroke-linecap", False) else None

                element.stroke_linejoin(element_attrs["stroke-linejoin"]) \
                    if element_attrs.get("stroke-linejoin", False) else None

                element.stroke_miterlimit(float(element_attrs["stroke-miterlimit"])) \
                    if element_attrs.get("stroke-miterlimit", False) else None

                element.stroke_dashoffset(float(element_attrs["stroke-dashoffset"])) \
                    if element_attrs.get("stroke-dashoffset", False) else None

                element.fill_rule(element_attrs["fill-rule"]) \
                    if element_attrs.get("fill-rule", False) else None

                if element_attrs.get("stroke-dasharray", False):
                    d = dict()
                    exec("x=(" + element_attrs["stroke-dasharray"] + ")", d)
                    element.stroke_dasharray(d['x'])
                
                if element:
                    groups[item] = element
                # input()

    def _apply_transforms(self, element, transforms):
        d = dict()
        for transform in transforms:
            if "translate" in transform:
                exec(transform.replace("translate", "x=").replace(" ", ","), d)
                if type(d['x']) == tuple:
                    element.translate(*d['x'], 0)
                else:
                    element.translate(d['x'], 0, 0)
            elif "scale" in transform:
                exec(transform.replace("scale", "x=").replace(" ", ","), d)
                if type(d['x']) == tuple:
                    element.scale(d['x'][0], d['x'][1], 1, [0, 0, 0], True)
                else:
                    element.scale(d['x'], d['x'], 1, [0, 0, 0], True)
            elif "rotate" in transform:
                exec(transform.replace("rotate", "x=").replace(" ", ","), d)
                if type(d['x']) == tuple:
                    element.rotate(d['x'][0], [0, 0, 1],
                                   [d['x'][1], d['x'][2], 0], True)
                else:
                    element.rotate(d['x'], [0, 0, 1], [0, 0, 0], True)
            elif "skewX" in transform:
                exec(transform.replace("skewX", "x=").replace(" ", ","), d)
                element.matrix(
                    np.array([
                        [1, math.tan((math.pi / 180) * d['x'][0]), 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1.0],
                    ]))
            elif "skewY" in transform:
                exec(transform.replace("skewY", "x=").replace(" ", ","), d)
                element.matrix(
                    np.array([
                        [1, 0, 0, 0],
                        [math.tan((math.pi / 180) * d['x'][0]), 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1.0],
                    ]))
            else:
                exec(transform.replace("matrix", "x=").replace(" ", ","), d)
                element.matrix(
                    np.array([
                        [d['x'][0], d['x'][2], 0, d['x'][4]],
                        [d['x'][1], d['x'][3], 0, d['x'][5]],
                        [0, 0, 1.0, 0],
                        [0, 0, 0, 1.0],
                    ]))
        

