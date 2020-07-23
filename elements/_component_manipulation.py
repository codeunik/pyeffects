from ._arc2bezier import _arc2bezier
from .svgpathtools import Arc, CubicBezier, Line, QuadraticBezier


def _split_bezier(curve, r):
    # De Casteljau's Subdivision Algorithm
    # https://www.clear.rice.edu/comp360/lectures/old/BezSubd.pdf
    if r == 0 or r == 1:
        return [curve]
    p0 = curve.start
    p1 = curve.control1
    p2 = curve.control2
    p3 = curve.end

    d = (1 - r) * p1 + r * p2
    q0 = p0
    q1 = (1 - r) * p0 + r * p1
    q2 = (1 - r) * q1 + r * d

    r3 = p3
    r2 = (1 - r) * p2 + r * p3
    r1 = (1 - r) * d + r * r2

    q3 = r0 = (1 - r) * q2 + r * r1
    return [CubicBezier(q0, q1, q2, q3), CubicBezier(r0, r1, r2, r3)]


def _split_line(line, r):
    if r == 0 or r == 1:
        return [line]
    p = line.point(r)
    return [Line(line.start, p), Line(p, line.end)]


def _update_comp_len_list(l, index):
    l[index] = [l[index][0] / 2, l[index][1]]
    l.insert(index + 1, l[index])
    for i in range(index + 1, len(l)):
        l[i][1] += 1


def _replace_by_beziers(path):
    i = 0
    while i < len(path):
        if type(path[i]) == Arc:
            px = path[i].start.real
            py = path[i].start.imag
            cx = path[i].end.real
            cy = path[i].end.imag
            rx = path[i].radius.real
            ry = path[i].radius.imag
            xAxisRotation = path[i].rotation
            largeArcFlag = int(path[i].large_arc)
            sweepFlag = int(path[i].sweep)
            curves = _arc2bezier(px, py, cx, cy, rx, ry, xAxisRotation,
                                 largeArcFlag, sweepFlag)
            curves[0] = [
                round(path[i].start.real, 3),
                round(path[i].start.imag, 3)
            ] + curves[0]
            del path[i]
            for j in range(1, len(curves)):
                temp = curves[j - 1][-2:]
                curves[j] = temp + curves[j]
            for curve in reversed(curves):
                path.insert(
                    i,
                    CubicBezier(*[
                        complex(curve[2 * j], curve[2 * j + 1])
                        for j in range(len(curve) // 2)
                    ]))
        elif type(path[i]) == QuadraticBezier:
            q0 = path[i].start
            q1 = path[i].control
            q2 = path[i].end

            p0 = q0
            p3 = q2
            p1 = q0 + 2 * (q1 - q0) / 3
            p2 = q2 + 2 * (q1 - q2) / 3
            path[i] = CubicBezier(p0, p1, p2, p3)

        i += 1
    return path
