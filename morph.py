from copy import deepcopy

import numpy as np
from scipy.optimize import linear_sum_assignment

from . import ease
from .elements.group import Group
from .elements.path import Path
from .elements.svgpathtools import CubicBezier, Line
from .tween import Tween


class morph(Tween):
    def __init__(self, morph_to, ease=ease.linear, **kwargs):
        self.metrics = {"distance": self.bbox_center_dist}

        self.morph_to = morph_to
        self.info = dict()
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if t == 0:
            mfg = Group()
            mtg = Group()
            if isinstance(self.elements, Group):
                for item in self.elements:
                    mfg.append(deepcopy(item).abs_transform())
            else:
                mfg.append(deepcopy(self.elements).abs_transform())

            if isinstance(self.morph_to, Group):
                for item in self.morph_to:
                    mtg.append(deepcopy(item).abs_transform())
            else:
                mtg.append(deepcopy(self.morph_to).abs_transform())

            self.maps_for_morph(mfg, mtg)
        elif 0 < t <= 1:
            et = self.ease(t)  # should not use yoyo type ease
            for k in self.info:
                mf_segs = self.info[k]["from_segs"]
                mf_stroke = self.info[k]["from_props"]["stroke"]
                mf_fill = self.info[k]["from_props"]["fill"]
                mf_stroke_width = self.info[k]["from_props"]["stroke_width"]
                mf_opacity = self.info[k]["from_props"]["opacity"]
                mf_fill_opacity = self.info[k]["from_props"]["fill_opacity"]
                mf_stroke_opacity = self.info[k]["from_props"][
                    "stroke_opacity"]
                mf_stroke_linecap = self.info[k]["from_props"][
                    "stroke_linecap"]
                mf_stroke_linejoin = self.info[k]["from_props"][
                    "stroke_linejoin"]
                mf_stroke_dasharray = self.info[k]["from_props"][
                    "stroke_dasharray"]
                mf_fill_rule = self.info[k]["from_props"]["fill_rule"]
                mf_stroke_miterlimit = self.info[k]["from_props"][
                    "stroke_miterlimit"]
                mf_stroke_dashoffset = self.info[k]["from_props"][
                    "stroke_dashoffset"]

                mt_segs = self.info[k]["to_segs"]
                mt_stroke = self.info[k]["to_props"]["stroke"]
                mt_fill = self.info[k]["to_props"]["fill"]
                mt_stroke_width = self.info[k]["to_props"]["stroke_width"]
                mt_opacity = self.info[k]["to_props"]["opacity"]
                mt_fill_opacity = self.info[k]["to_props"]["fill_opacity"]
                mt_stroke_opacity = self.info[k]["to_props"]["stroke_opacity"]
                mt_stroke_linecap = self.info[k]["to_props"]["stroke_linecap"]
                mt_stroke_linejoin = self.info[k]["to_props"][
                    "stroke_linejoin"]
                mt_stroke_dasharray = self.info[k]["to_props"][
                    "stroke_dasharray"]
                mt_fill_rule = self.info[k]["to_props"]["fill_rule"]
                mt_stroke_miterlimit = self.info[k]["to_props"][
                    "stroke_miterlimit"]
                mt_stroke_dashoffset = self.info[k]["to_props"][
                    "stroke_dashoffset"]

                data = []
                for j in range(len(mf_segs)):
                    for i in range(len(mf_segs[j])):
                        data.append(
                            CubicBezier(((1 - et) * mf_segs[j][i].start +
                                         et * mt_segs[j][i].start),
                                        ((1 - et) * mf_segs[j][i].control1 +
                                         et * mt_segs[j][i].control1),
                                        ((1 - et) * mf_segs[j][i].control2 +
                                         et * mt_segs[j][i].control2),
                                        ((1 - et) * mf_segs[j][i].end +
                                         et * mt_segs[j][i].end)))
                p = self.elements[i] if type(
                    self.elements) == Group else self.elements
                p.data(data)
                p.stroke(self.interpolate(et, mf_stroke, mt_stroke))
                p.stroke_width(
                    self.interpolate(et, mf_stroke_width, mt_stroke_width))
                p.fill(self.interpolate(et, mf_fill, mt_fill))
                p.opacity(self.interpolate(et, mf_opacity, mt_opacity))
                p.fill_opacity(
                    self.interpolate(et, mf_fill_opacity, mt_fill_opacity))
                p.stroke_opacity(
                    self.interpolate(et, mf_stroke_opacity, mt_stroke_opacity))
                p.stroke_linecap(
                    self.interpolate(et, mf_stroke_linecap, mt_stroke_linecap))
                p.stroke_linejoin(
                    self.interpolate(et, mf_stroke_linejoin,
                                     mt_stroke_linejoin))
                p.stroke_dasharray(
                    self.interpolate(et, mf_stroke_dasharray,
                                     mt_stroke_dasharray))
                p.fill_rule(self.interpolate(et, mf_fill_rule, mt_fill_rule))
                p.stroke_miterlimit(
                    self.interpolate(et, mf_stroke_miterlimit,
                                     mt_stroke_miterlimit))
                p.stroke_dashoffset(
                    self.interpolate(et, mf_stroke_dashoffset,
                                     mt_stroke_dashoffset))
        return [self.elements]

    def interpolate(self, t, p1, p2):
        if type(p2) == str:
            return p2
        elif type(p1) != str:
            return (1 - t) * p1 + t * p2

    def maps_for_morph(self, g1, g2):
        g1i, g2i = self.map_paths(g1, g2, self.bbox_center_dist)
        for i in range(len(g1i)):
            mfi = g1i[i]
            mti = g2i[i]
            p1 = g1[mfi]
            pp1 = self.get_props(p1)
            p2 = g2[mti]
            pp2 = self.get_props(p2)

            s1i, s2i = self.map_segs(p1, p2, self.bbox_area_dist)
            sp1 = p1.continuous_subpaths()
            sp2 = p2.continuous_subpaths()

            self.info[i] = dict()
            self.info[i]["from_props"] = pp1
            self.info[i]["to_props"] = pp2
            self.info[i]["from_segs"] = list()
            self.info[i]["to_segs"] = list()
            for j in range(len(s1i)):
                mfp = Path(sp1[s1i[j]])
                if s2i[j] is not None:
                    mtp = Path(sp2[s2i[j]])
                    self.one_to_one_morph(mfp, mtp, i)
                else:
                    self.one_to_one_morph(mfp, None, i)

    def map_paths(self, p1, p2, metric):
        cp1 = deepcopy(p1)
        cp2 = deepcopy(p2)
        p1_indices = []
        p2_indices = []
        flag = True
        while flag:
            cp1i, cp2i, _ = self.set_distance(cp1, cp2, metric)
            if len(p1) >= len(p2):
                p1_indices.extend([p1.index(cp1[i]) for i in cp1i])
                p2_indices.extend(cp2i)
                for i in sorted(cp1i, reverse=True):
                    cp1.pop(i)
            else:
                p1_indices.extend(cp1i)
                p2_indices.extend([p2.index(cp2[i]) for i in cp2i])
                for i in sorted(cp2i, reverse=True):
                    cp2.pop(i)
            flag = True if cp1 and cp2 else False
        return p1_indices, p2_indices

    def map_segs(self, p1, p2, metric):
        p1_bbox = p1.bounding_box()
        p1_bbox_area = (p1_bbox[1] - p1_bbox[0]) * (p1_bbox[3] - p1_bbox[2])
        p2_bbox = p2.bounding_box()
        p2_bbox_area = (p2_bbox[1] - p2_bbox[0]) * (p2_bbox[3] - p2_bbox[2])

        p1s = p1.continuous_subpaths()
        p2s = p2.continuous_subpaths()

        pop_indices = []
        for i in range(len(p1s)):
            ps_bbox = p1s[i].bounding_box()
            ps_bbox_area = (ps_bbox[1] - ps_bbox[0]) * (ps_bbox[3] -
                                                        ps_bbox[2])
            if ps_bbox_area / p1_bbox_area <= 0.05:
                pop_indices.append(i)
        for i in reversed(pop_indices):
            p1s.pop(i)

        pop_indices = []
        for i in range(len(p2s)):
            ps_bbox = p2s[i].bounding_box()
            ps_bbox_area = (ps_bbox[1] - ps_bbox[0]) * (ps_bbox[3] -
                                                        ps_bbox[2])
            if ps_bbox_area / p2_bbox_area <= 0.05:
                pop_indices.append(i)
        for i in reversed(pop_indices):
            p2s.pop(i)

        if len(p1s) <= len(p2s):
            p1si, p2si = self.map_paths(p1s, p2s, metric)
        else:
            p1si = []
            p2si = []
            i1, i2, _ = self.set_distance(p1s, p2s, metric)
            p1si.extend(i1)
            p2si.extend(i2)
            for i in range(len(p1s)):
                if i not in i1:
                    p1si.append(i)
                    p2si.append(None)

        return p1si, p2si

    def get_props(self, path):
        return {
            "stroke": path._stroke,
            "fill": path._fill,
            "stroke_width": path._stroke_width,
            "opacity": path._opacity,
            "fill_opacity": path._fill_opacity,
            "stroke_opacity": path._stroke_opacity,
            "stroke_linecap": path._stroke_linecap,
            "stroke_linejoin": path._stroke_linejoin,
            "stroke_dasharray": path._stroke_dasharray,
            "fill_rule": path._fill_rule,
            "stroke_miterlimit": path._stroke_miterlimit,
            "stroke_dashoffset": path._stroke_dashoffset,
        }

    def bbox_center_dist(self, s1, s2):
        if type(s1) != Path:
            s1 = Path(s1)
        if type(s2) != Path:
            s2 = Path(s2)
        bbox1 = s1.bbox()
        bbox2 = s2.bbox()
        center1 = bbox1.sum(axis=0) / 2
        center2 = bbox2.sum(axis=0) / 2
        return np.linalg.norm(center1 - center2)

    def bbox_area_dist(self, s1, s2):
        if type(s1) != Path:
            s1 = Path(s1)
        if type(s2) != Path:
            s2 = Path(s2)

        bbox1 = s1.bbox()
        width1 = bbox1[1][0] - bbox1[0][0]
        height1 = bbox1[1][1] - bbox1[0][1]
        area1 = width1 * height1

        bbox2 = s2.bbox()
        width2 = bbox2[1][0] - bbox2[0][0]
        height2 = bbox2[1][1] - bbox2[0][1]
        area2 = width2 * height2

        return abs(area2 - area1)

    def one_to_one_morph(self, mf, mt, i):
        if mt is None:
            mt = deepcopy(mf)
            mt.scale(0.0001, 0.0001)

        mfc = deepcopy(mf)
        mtc = deepcopy(mt)

        mft = mfc.to_pos(0, 0)
        mtt = mtc.to_pos(0, 0)
        mfc.translate(*mft)
        mtc.translate(*mtt)

        mfc_bbox = mfc.bbox()
        mfc_width = mfc_bbox[1][0] - mfc_bbox[0][0]
        mfc_height = mfc_bbox[1][1] - mfc_bbox[0][1]

        mtc_bbox = mtc.bbox()
        mtc_width = mtc_bbox[1][0] - mtc_bbox[0][0]
        mtc_height = mtc_bbox[1][1] - mtc_bbox[0][1]

        mtcbymfc_width = mtc_width / mfc_width
        mtcbymfc_height = mtc_height / mfc_height

        mfc.scale(mtcbymfc_width, mtcbymfc_height)
        mfc = mfc.abs_transform()
        mtc = mtc.abs_transform()

        mfpp = self.get_path_points(mfc)
        mtpp = self.get_path_points(mtc)
        mfi, mti = self.get_closest_points(mfpp, mtpp, self.point_distance)
        mfc.shift_index(mfi)
        mtc.shift_index(mti)
        mfpp = self.get_path_points(mfc)
        mtpp = self.get_path_points(mtc)

        mfcll = CircularLinkedList().add_by_list(self.get_seg_ratios(mfc))
        mtcll = CircularLinkedList().add_by_list(self.get_seg_ratios(mtc))
        mp = MatchPoints(mfcll, mtcll)
        path_to_split, split_ratios = mp.get_split_ratios()

        if path_to_split == 1:
            self.split_path(mfc, split_ratios)
        else:
            self.split_path(mtc, split_ratios)

        mfc.scale(1 / mtcbymfc_width, 1 / mtcbymfc_height)
        mfc.translate(*-mft)
        mf = mfc.abs_transform()

        mtc.translate(*-mtt)
        mt = mtc.abs_transform()

        self.line2bezier(mf)
        self.line2bezier(mt)

        self.info[i]["from_segs"].append(mf)
        self.info[i]["to_segs"].append(mt)

    def point_distance(self, p1, p2):
        if type(p1) == complex and type(p2) == complex:
            return ((p1.real - p2.real)**2 + (p1.imag - p2.imag)**2)**0.5
        elif type(p1) == np.ndarray and type(p2) == np.ndarray:
            return np.linalg.norm(p1 - p2)

    def set_distance(self, A, B, d):
        dist = []
        for i in range(len(A)):
            dist.append([])
            for j in range(len(B)):
                dist[i].append(d(A[i], B[j]))
        dist = np.array(dist)
        row_indices, col_indices = linear_sum_assignment(dist)
        return row_indices, col_indices, dist[row_indices, col_indices].sum()

    def get_closest_points(self, A, B, d):
        dist = []
        for i in range(len(A)):
            dist.append([])
            for j in range(len(B)):
                dist[i].append(d(A[i], B[j]))
        dist = np.array(dist)
        ai, bi = np.unravel_index(dist.argmin(), dist.shape)
        return ai, bi

    def get_path_points(self, path):
        points = []
        for seg in path:
            points.append(seg.start)
        return points

    def get_seg_ratios(self, path):
        seg_lengths = []
        path_length = path.length()
        for seg in path:
            seg_lengths.append(seg.length() / path_length)
        return seg_lengths

    def split_bezier(self, curve, r):
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

    def split_line(self, line, r):
        if r == 0 or r == 1:
            return [line]
        p = line.point(r)
        return [Line(line.start, p), Line(p, line.end)]

    def split_path(self, path, breakpoints):
        for breakpoint in breakpoints:
            i, t = breakpoint
            seg = path.pop(i)
            if type(seg) == CubicBezier:
                parts = self.split_bezier(seg, t)
            elif type(seg) == Line:
                parts = self.split_line(seg, t)
            for seg in reversed(parts):
                path.insert(i, seg)

    def line2bezier(self, path):
        for i in range(len(path)):
            if type(path[i]) == Line:
                path[i] = CubicBezier(path[i].start, path[i].start,
                                      path[i].end, path[i].end)


# 1. get abs pts of both source and dest
# 4. rotate and scale morph_to minimize linear_sum_assignment and identify the closest points (take avg of the control points of beizier curve) and save the total distance
# 6. determine the shapeindex and then using proportion equate the number of points of both source and dest
# 7. interpolate

# for more than one curves

# if allow duplicate then create duplicate elements for morphing if dest have more path else more paths appear from nothing


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class CircularLinkedList:
    def __init__(self):
        self.zeroth_node = None
        self.current_node = None
        self.total_nodes = 0
        self.index = 0

    def add(self, data):
        node = Node(data)
        if self.current_node is None:
            self.current_node = node
        if self.zeroth_node is None:
            self.zeroth_node = node
        node.next = self.current_node.next
        node.prev = self.current_node
        self.current_node.next = node
        self.current_node.next.prev = node
        self.current_node = node
        self.total_nodes += 1
        self.index += 1
        return self

    def delete(self):
        self.current_node.prev.next = self.current_node.next
        self.current_node.next.prev = self.current_node.prev
        self.current_node = self.current_node.next
        self.total_nodes -= 1
        return self

    def add_by_list(self, l):
        for data in l:
            self.add(data)
        return self

    def data(self):
        return self.current_node.data

    def get_index(self):
        return self.index

    def next(self):
        self.index = (self.index + 1) % self.total_nodes
        self.current_node = self.current_node.next
        return self

    def prev(self):
        self.index = (self.index - 1) % self.total_nodes
        self.current_node = self.current_node.prev
        return self

    def goto_index(self, n):
        self.current_node = self.zeroth_node
        self.index = 0
        while self.index != n:
            self.next()
        return self

    def get_all_data(self):
        self.goto_index(0)
        all_data = []
        flag = True
        while flag:
            all_data.append(self.data())
            self.next()
            flag = False if self.index == 0 else True
        return all_data

    def length(self):
        return self.total_nodes


class MatchPoints:
    def __init__(self, cll1, cll2):
        self.is_cll1_short = True if cll1.length() <= cll2.length() else False
        if self.is_cll1_short:
            self.cll1 = cll1
            self.n1 = self.cll1.length()
            self.cll2 = cll2
            self.n2 = self.cll2.length()
        else:
            self.cll1 = cll2
            self.n1 = self.cll1.length()
            self.cll2 = cll1
            self.n2 = self.cll2.length()
        self.bonds = [(0, 0)]
        self.split_ratios = []

    def find_bonds(self):
        self.cll1.goto_index(0)
        self.cll2.goto_index(0)
        d1 = d2 = 0
        j = 1
        last_j = 0
        for i in range(1, self.cll1.length()):
            d1 += self.cll1.data()
            while 1 <= j < self.cll2.length():
                d2 += self.cll2.data()
                if self.cll1.length() - i >= self.cll2.length() - j:
                    self.bonds.append((i, j))
                    last_j = j
                    j += 1
                    self.cll2.next()
                    break
                elif d2 >= d1:
                    if d2 - d1 > d1 - d2 + self.cll2.data() and last_j != j - 1:
                        self.bonds.append((i, j - 1))
                        last_j = j - 1
                        d2 -= self.cll2.data()
                    else:
                        self.bonds.append((i, j))
                        last_j = j
                        j += 1
                        self.cll2.next()
                    break
                j += 1
                self.cll2.next()
            self.cll1.next()

    def get_bonds(self):
        self.find_bonds()
        if self.is_cll1_short:
            return self.bonds
        else:
            return [(i1, i0) for i0, i1 in self.bonds]

    def get_split_ratios(self):
        self.find_bonds()
        bonds = self.bonds.copy()
        bonds.append(self.bonds[0])
        for i in range(len(bonds) - 1):
            unattended_points = (bonds[i + 1][1] - bonds[i][1]) % self.n2
            if unattended_points > 1:
                lengths = [0]
                for j in reversed(
                        list(
                            map(lambda k: (bonds[i][1] + k) % self.n2,
                                range(unattended_points)))):
                    cl = self.cll2.goto_index(j).data()
                    cl += lengths[0]
                    lengths.insert(0, cl)
                lengths.pop(-1)
                lengths.pop(-1)
                lengths = np.array(lengths)

                indices = []
                ratios = []
                for j in map(lambda k: (bonds[i][1] + k) % self.n2,
                             range(unattended_points - 1)):
                    cl = self.cll2.goto_index(j).data()
                    indices.append(j % self.n2)
                    ratios.append(cl)
                ratios = np.array(ratios) / lengths
                self.split_ratios.extend(list(zip(indices, ratios)))
        return 1 if self.is_cll1_short else 2, self.split_ratios
