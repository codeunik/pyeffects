import math


def _mapToEllipse(point, rx, ry, cosphi, sinphi, centerx, centery):
    x = point[0]
    y = point[1]
    x *= rx
    y *= ry

    xp = cosphi * x - sinphi * y
    yp = sinphi * x + cosphi * y

    return [xp + centerx, yp + centery]


def _approxUnitArc(ang1, ang2):
    # If 90 degree circular arc, use a constant
    # as derived from http://spencermortensen.com/articles/bezier-circle

    if ang2 == 1.5707963267948966:
        a = 0.551915024494
    elif ang2 == -1.5707963267948966:
        a = -0.551915024494
    else:
        a = 4 / 3 * math.tan(ang2 / 4)

    x1 = math.cos(ang1)
    y1 = math.sin(ang1)
    x2 = math.cos(ang1 + ang2)
    y2 = math.sin(ang1 + ang2)

    return [[x1 - y1 * a, y1 + x1 * a], [x2 + y2 * a, y2 - x2 * a], [x2, y2]]


def _vectorAngle(ux, uy, vx, vy):
    if (ux * vy - uy * vx < 0):
        sign = -1
    else:
        sign = 1

    dot = ux * vx + uy * vy

    if (dot > 1):
        dot = 1

    if (dot < -1):
        dot = -1

    return sign * math.acos(dot)


def _getArcCenter(px, py, cx, cy, rx, ry, largeArcFlag, sweepFlag, sinphi,
                  cosphi, pxp, pyp):
    rxsq = rx**2
    rysq = ry**2
    pxpsq = pxp**2
    pypsq = pyp**2

    radicant = (rxsq * rysq) - (rxsq * pypsq) - (rysq * pxpsq)

    if (radicant < 0):
        radicant = 0

    if largeArcFlag == sweepFlag:
        flag = -1
    else:
        flag = 1
    radicant /= (rxsq * pypsq) + (rysq * pxpsq)
    radicant = math.sqrt(radicant) * flag

    centerxp = radicant * rx / ry * pyp
    centeryp = radicant * -ry / rx * pxp

    centerx = cosphi * centerxp - sinphi * centeryp + (px + cx) / 2
    centery = sinphi * centerxp + cosphi * centeryp + (py + cy) / 2

    vx1 = (pxp - centerxp) / rx
    vy1 = (pyp - centeryp) / ry
    vx2 = (-pxp - centerxp) / rx
    vy2 = (-pyp - centeryp) / ry

    ang1 = _vectorAngle(1, 0, vx1, vy1)
    ang2 = _vectorAngle(vx1, vy1, vx2, vy2)

    TAU = 2 * math.pi
    if (sweepFlag == 0 and ang2 > 0):
        ang2 -= TAU

    if (sweepFlag == 1 and ang2 < 0):
        ang2 += TAU

    return [centerx, centery, ang1, ang2]


def _arc2bezier(px,
                py,
                cx,
                cy,
                rx,
                ry,
                xAxisRotation=0,
                largeArcFlag=0,
                sweepFlag=0):
    curves = []

    if (rx == 0 or ry == 0):
        return []

    TAU = 2 * math.pi
    sinphi = math.sin(xAxisRotation * TAU / 360)
    cosphi = math.cos(xAxisRotation * TAU / 360)

    pxp = cosphi * (px - cx) / 2 + sinphi * (py - cy) / 2
    pyp = -sinphi * (px - cx) / 2 + cosphi * (py - cy) / 2

    if (pxp == 0 and pyp == 0):
        return []

    rx = abs(rx)
    ry = abs(ry)

    lambda_ = (pxp**2) / (rx**2) + (pyp**2) / (ry**2)

    if (lambda_ > 1):
        rx *= math.sqrt(lambda_)
        ry *= math.sqrt(lambda_)

    [centerx, centery, ang1,
     ang2] = _getArcCenter(px, py, cx, cy, rx, ry, largeArcFlag, sweepFlag,
                           sinphi, cosphi, pxp, pyp)

    # If 'ang2' == 90.0000000001, then `ratio` will evaluate to
    # 1.0000000001. This causes `segments` to be greater than one, which is an
    # unecessary split, and adds extra points to the bezier curve. To alleviate
    # this issue, we round to 1.0 when the ratio is close to 1.0.
    ratio = abs(ang2) / (TAU / 4)
    if (abs(1.0 - ratio) < 0.0000001):
        ratio = 1.0

    segments = max(math.ceil(ratio), 1)

    ang2 /= segments

    for i in range(segments):
        curves.append(_approxUnitArc(ang1, ang2))
        ang1 += ang2

    beziers = []
    for curve in curves:
        x1, y1 = _mapToEllipse(curve[0], rx, ry, cosphi, sinphi, centerx,
                               centery)
        x2, y2 = _mapToEllipse(curve[1], rx, ry, cosphi, sinphi, centerx,
                               centery)
        x, y = _mapToEllipse(curve[2], rx, ry, cosphi, sinphi, centerx,
                             centery)
        beziers.append([
            round(x1, 3),
            round(y1, 3),
            round(x2, 3),
            round(y2, 3),
            round(x, 3),
            round(y, 3)
        ])
    return beziers
