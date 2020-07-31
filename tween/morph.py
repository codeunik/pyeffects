from copy import deepcopy

import numpy as np
from scipy.optimize import linear_sum_assignment

from . import ease
from ..elements.frame import Scene
from ..elements.group import Group
from ..elements.path import Path
from ..elements.svgpathtools import CubicBezier, Line
from .tween import Tween


class morph(Tween):
    def __init__(self, morph_to, ease=ease.linear, **kwargs):
        self.metrics = {"distance": self.bbox_center_dist}

        self.morph_to = morph_to
        self.info = dict()
        self.ease = ease
        super().__init__(**kwargs)

    def update(self, t):
        if not isinstance(self.elements, Group):
            raise Exception("Morph from elements must be in a Group.")
        if t == 0:
            mfg = Group()
            mtg = Group()
            if isinstance(self.elements, Group):
                for item in self.elements:
                    item = item._apply_static_transform()
                    mfg.append(deepcopy(item)._apply_static_transform())
            else:
                mfg.append(deepcopy(self.elements)._apply_static_transform())

            if isinstance(self.morph_to, Group):
                for item in self.morph_to:
                    mtg.append(deepcopy(item)._apply_static_transform())
            else:
                mtg.append(deepcopy(self.morph_to)._apply_static_transform())

            self.maps_for_morph(mfg, mtg)
        elif 0 < t <= 1:
            paths = []
            et = self.ease(t)    # should not use yoyo type ease
            for k in self.info:
                mf_segs = self.info[k]["from_paths"]
                mf_stroke = self.info[k]["from_props"]["stroke"]
                mf_fill = self.info[k]["from_props"]["fill"]
                mf_stroke_width = self.info[k]["from_props"]["stroke_width"]
                mf_opacity = self.info[k]["from_props"]["opacity"]
                mf_fill_opacity = self.info[k]["from_props"]["fill_opacity"]
                mf_stroke_opacity = self.info[k]["from_props"]["stroke_opacity"]

                mt_segs = self.info[k]["to_paths"]
                mt_stroke = self.info[k]["to_props"]["stroke"]
                mt_fill = self.info[k]["to_props"]["fill"]
                mt_stroke_width = self.info[k]["to_props"]["stroke_width"]
                mt_opacity = self.info[k]["to_props"]["opacity"]
                mt_fill_opacity = self.info[k]["to_props"]["fill_opacity"]
                mt_stroke_opacity = self.info[k]["to_props"]["stroke_opacity"]

                data = []
                for j in range(len(mf_segs)):
                    for i in range(len(mf_segs[j])):
                        data.append(
                            CubicBezier(
                                ((1 - et) * mf_segs[j][i].start + et * mt_segs[j][i].start),
                                ((1 - et) * mf_segs[j][i].control1 + et * mt_segs[j][i].control1),
                                ((1 - et) * mf_segs[j][i].control2 + et * mt_segs[j][i].control2),
                                ((1 - et) * mf_segs[j][i].end + et * mt_segs[j][i].end)))
                p = Path()
                p.set_segments(data)
                p.stroke(self.interpolate(et, mf_stroke, mt_stroke))
                p.stroke_width(self.interpolate(et, mf_stroke_width, mt_stroke_width))
                p.fill(self.interpolate(et, mf_fill, mt_fill))
                p.opacity(self.interpolate(et, mf_opacity, mt_opacity))
                p.fill_opacity(self.interpolate(et, mf_fill_opacity, mt_fill_opacity))
                p.stroke_opacity(self.interpolate(et, mf_stroke_opacity, mt_stroke_opacity))
                paths.append(p)
            self.elements.clear()
            self.elements.extend(paths)
        return [self.elements]

    def interpolate(self, t, p1, p2):
        types = [int, float, np.ndarray]
        if type(p1) in types and type(p2) in types:
            return (1 - t) * p1 + t * p2
        return p2

    def maps_for_morph(self, g1, g2):
        g1i, g2i = self.map_paths(g1, g2, self.bbox_center_dist)
        for i in range(len(g1i)):
            mfi = g1i[i]
            mti = g2i[i]
            p1 = g1[mfi]
            pp1 = self.get_props(p1)
            p2 = g2[mti]
            pp2 = self.get_props(p2)

            s1i, s2i = self.map_segs(p1._data_2d, p2._data_2d, self.bbox_area_dist)

            sp1 = p1._data_2d.continuous_subpaths()
            sp2 = p2._data_2d.continuous_subpaths()
            self.info[i] = dict()
            self.info[i]["from_props"] = pp1
            self.info[i]["to_props"] = pp2
            self.info[i]["from_paths"] = list()
            self.info[i]["to_paths"] = list()
            for j in range(len(s1i)):
                mfp = Path(sp1[s1i[j]])
                if s2i[j] is not None:
                    mtp = Path(sp2[s2i[j]])
                    self.one_to_one_morph(mfp, mtp, i)
                else:
                    self.one_to_one_morph(mfp, None, i)

    def map_paths(self, g1, g2, metric):
        cg1 = deepcopy(g1)
        cg2 = deepcopy(g2)
        g1_indices = []
        g2_indices = []
        flag = True
        while flag:
            cg1i, cg2i, _ = self.set_distance(cg1, cg2, metric)
            if len(g1) >= len(g2):
                g1_indices.extend([
                    j for i in cg1i for j in range(len(g1))
                    if g1[j]._data_2d == cg1[i]._data_2d and j not in g1_indices
                ])
                g2_indices.extend(cg2i)
                for i in sorted(cg1i, reverse=True):
                    cg1.pop(i)
            else:
                g1_indices.extend(cg1i)
                g2_indices.extend([
                    j for i in cg2i for j in range(len(g2))
                    if g2[j]._data_2d == cg2[i]._data_2d and j not in g2_indices
                ])
                for i in sorted(cg2i, reverse=True):
                    cg2.pop(i)
            flag = True if cg1 and cg2 else False
        return g1_indices, g2_indices

    def map_segs(self, d1, d2, metric):
        d1_bbox = d1.bounding_box()
        d1_bbox_area = (d1_bbox[1] - d1_bbox[0]) * (d1_bbox[3] - d1_bbox[2])
        d2_bbox = d2.bounding_box()
        d2_bbox_area = (d2_bbox[1] - d2_bbox[0]) * (d2_bbox[3] - d2_bbox[2])

        d1s = d1.continuous_subpaths()
        d2s = d2.continuous_subpaths()

        pop_indices = []
        for i in range(len(d1s)):
            ds_bbox = d1s[i].bounding_box()
            ds_bbox_area = (ds_bbox[1] - ds_bbox[0]) * (ds_bbox[3] - ds_bbox[2])
            if ds_bbox_area / d1_bbox_area <= 0.05:
                pop_indices.append(i)
        for i in reversed(pop_indices):
            d1s.pop(i)

        pop_indices = []
        for i in range(len(d2s)):
            ds_bbox = d2s[i].bounding_box()
            ds_bbox_area = (ds_bbox[1] - ds_bbox[0]) * (ds_bbox[3] - ds_bbox[2])
            if ds_bbox_area / d2_bbox_area <= 0.05:
                pop_indices.append(i)
        for i in reversed(pop_indices):
            d2s.pop(i)

        d1s = [Path(d) for d in d1s]
        d2s = [Path(d) for d in d2s]
        if len(d1s) <= len(d2s):
            d1si, d2si = self.map_paths(d1s, d2s, metric)
        else:
            d1si = []
            d2si = []
            i1, i2, _ = self.set_distance(d1s, d2s, metric)
            d1si.extend(i1)
            d2si.extend(i2)
            for i in range(len(d1s)):
                if i not in i1:
                    d1si.append(i)
                    d2si.append(None)
        return d1si, d2si

    def get_props(self, path):
        return {
            "stroke": path._stroke,
            "fill": path._fill,
            "stroke_width": path._stroke_width,
            "opacity": path._opacity,
            "fill_opacity": path._fill_opacity,
            "stroke_opacity": path._stroke_opacity,
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

    def one_to_one_morph(self, mfp, mtp, i):
        if mtp is None:
            mtp = deepcopy(mfp)
            mtp.scale(0.0001, 0.0001)

        mfp = deepcopy(mfp)
        mtp = deepcopy(mtp)

        mft = mfp.to_pos(0, 0)
        mtt = mtp.to_pos(0, 0)
        mfp.translate(*mft)
        mtp.translate(*mtt)

        mfp_bbox = mfp.bbox()
        mfp_width = mfp_bbox[1][0] - mfp_bbox[0][0]
        mfp_height = mfp_bbox[1][1] - mfp_bbox[0][1]

        mtp_bbox = mtp.bbox()
        mtp_width = mtp_bbox[1][0] - mtp_bbox[0][0]
        mtp_height = mtp_bbox[1][1] - mtp_bbox[0][1]

        mtpbymfp_width = mtp_width / mfp_width
        mtpbymfp_height = mtp_height / mfp_height

        mfp.scale(mtpbymfp_width, mtpbymfp_height)
        mfp = mfp._apply_static_transform()
        mtp = mtp._apply_static_transform()

        mfd = mfp._data_2d
        mtd = mtp._data_2d

        mfdp = self.get_path_points(mfd)
        mtdp = self.get_path_points(mtd)
        mfi, mti = self.get_closest_points(mfdp, mtdp, self.point_distance)

        self.shift_index(mfd, mfi)
        self.shift_index(mtd, mti)

        mfcll = CircularLinkedList().add_by_list(self.get_seg_ratios(mfd))
        mtcll = CircularLinkedList().add_by_list(self.get_seg_ratios(mtd))
        mp = MatchPoints(mfcll, mtcll)
        path_to_split, split_ratios = mp.get_split_ratios()

        if path_to_split == 1:
            mfd = self.split_path(mfd, split_ratios)
        else:
            mtd = self.split_path(mtd, split_ratios)

        mfp = Path(mfd)
        mtp = Path(mtd)

        mfp.scale(1 / mtpbymfp_width, 1 / mtpbymfp_height)
        mfp.translate(-mft[0], -mft[1], 0)
        mfp = mfp._apply_static_transform()

        mtp.translate(-mtt[0], -mtt[1], 0)
        mtp = mtp._apply_static_transform()

        mfd = self.line2bezier(mfp._data_2d)
        mtd = self.line2bezier(mtp._data_2d)

        self.info[i]["from_paths"].append(mfd)
        self.info[i]["to_paths"].append(mtd)

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

    def get_path_points(self, d):
        points = []
        for seg in d:
            points.append(seg.start)
        return points

    def get_seg_ratios(self, d):
        seg_lengths = []
        path_length = d.length()
        for seg in d:
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

    def split_path(self, d, breakpoints):
        for breakpoint in breakpoints:
            i, t = breakpoint
            seg = d.pop(i)
            if type(seg) == CubicBezier:
                parts = self.split_bezier(seg, t)
            elif type(seg) == Line:
                parts = self.split_line(seg, t)
            for seg in reversed(parts):
                d.insert(i, seg)
        return d

    def line2bezier(self, d):
        for i in range(len(d)):
            if type(d[i]) == Line:
                d[i] = CubicBezier(d[i].start, d[i].start, d[i].end, d[i].end)
        return d

    def shift_index(self, d, index):
        for i in range(index):
            d.append(d.pop(0))


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
                        list(map(lambda k: (bonds[i][1] + k) % self.n2, range(unattended_points)))):
                    cl = self.cll2.goto_index(j).data()
                    cl += lengths[0]
                    if cl <= 0:
                        cl = 0.001
                    elif cl >= 0.999:
                        cl = 0.999
                    lengths.insert(0, cl)
                lengths.pop(-1)
                lengths.pop(-1)
                lengths = np.array(lengths)

                indices = []
                ratios = []
                for j in map(lambda k: (bonds[i][1] + k) % self.n2, range(unattended_points - 1)):
                    cl = self.cll2.goto_index(j).data()
                    indices.append(j % self.n2)
                    if cl <= 0:
                        cl = 0.001
                    elif cl >= 0.999:
                        cl = 0.999
                    ratios.append(cl)
                ratios = np.array(ratios) / lengths
                self.split_ratios.extend(list(zip(indices, ratios)))
        return 1 if self.is_cll1_short else 2, self.split_ratios
