from .path import Path
from .svgpathtools import parse_path


def Rectangle(x, y, width, height, rx=0, ry=0):
    return Path(rectangle(x, y, width, height, rx, ry))


def Circle(cx, cy, r):
    return Path(circle(cx, cy, r))


def Ellipse(cx, cy, rx, ry):
    return Path(ellipse(cx, cy, rx, ry))


def Line(x1, y1, x2, y2):
    return Path(line(x1, y1, x2, y2))


def rectangle(x, y, width, height, rx=0, ry=0):
    if rx * ry > 0:
        rectangle_path = f"M {x} {y+ry} l 0 {height-2*ry} a {rx} {ry} 0 0 0 {rx} {ry} l {width-2*rx} 0 a {rx} {ry} 0 0 0 {rx} {-ry} l 0 {-height+2*ry} a {rx} {ry} 0 0 0 {-rx} {-ry} l {-width+2*rx} 0 a {rx} {ry} 0 0 0 {-rx} {ry}"
    else:
        rectangle_path = f"M {x} {y} l 0 {height} l {width} 0 l 0 {-height} z"
    return rectangle_path


def circle(cx, cy, r):
    circle_path = f"M{cx-r},{cy} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0"
    return circle_path


def ellipse(cx, cy, rx, ry):
    ellipse_path = f"M{cx-rx},{cy} a{rx},{ry} 0 1,0 {2*rx},0 a{rx},{ry} 0 1,0 {-2*rx},0"
    return ellipse_path


def line(x1, y1, x2, y2):
    line_path = f"M{x1},{y1} L{x2},{y2}"
    return line_path
