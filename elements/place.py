import numpy as np


class Place:
    def anchor(self, element, anchor, abs=False):
        bbox = element.bbox()
        anchor = anchor if abs else (1 - anchor) * bbox[0] + anchor * bbox[1]
        return anchor

    def to_pos(self, pos_x, pos_y, pos_z=0, anchor=[0.5, 0.5, 0.5]):
        anchor = np.array([*anchor, 1])
        anchor = self.anchor(self, anchor)
        return np.array(
            [pos_x - anchor[0], pos_y - anchor[1], pos_z - anchor[2]])

    def to_relative_of(self,
                       target,
                       target_anchor=[0.5, 0.5, 0.5],
                       anchor=[0.5, 0.5, 0.5],
                       fix=[0, 0, 0],
                       offset=[0, 0, 0]):
        anchor = np.array([*anchor, 1])
        anchor = self.anchor(self, anchor)
        target_anchor = np.array([*target_anchor, 1])
        target_anchor = self.anchor(target, target_anchor)

        anchor[0] = target_anchor[0] if fix[0] else anchor[0]
        anchor[1] = target_anchor[1] if fix[0] else anchor[1]
        anchor[2] = target_anchor[2] if fix[0] else anchor[2]
        return np.array([
            target_anchor[0] - anchor[0] + offset[0],
            target_anchor[1] - anchor[1] + offset[1],
            target_anchor[2] - anchor[2] + offset[2],
        ])

    def place_at_pos(self, pos_x, pos_y, pos_z=0, anchor=[0.5, 0.5, 0.5]):
        self.translate(*self.to_pos(pos_x, pos_y, pos_z, anchor))
        return self

    def place_at_relative_of(self,
                             target,
                             target_anchor=[0.5, 0.5, 0.5],
                             anchor=[0.5, 0.5, 0.5],
                             fix=[0, 0, 0],
                             offset=[0, 0, 0]):

        self.translate(
            *self.to_relative_of(target, target_anchor, anchor, fix, offset))
        return self
