from .animation import *
from pyeffects import g
from copy import deepcopy
import numpy as np
from ..elements import Rectangle, Path, Mask
import uuid

class handwrite(Animation):
    def __init__(self, pointer, hand='hand', pen_tip='pen_tip', is_text=False):
        super().__init__()
        self.pointer = pointer
        g[self.pointer].opacity(0)
        self.hand = hand
        self.pen_tip = pen_tip
        self.is_text = is_text

    def animation(self):
        def after_update(ctx, **kwargs):
            path_end_point = kwargs['element'].point(ctx.et)
            pen_tip = g[self.pen_tip]
            bbox = g[self.hand].bbox()
            g[self.hand].translate(-bbox[0,0]-pen_tip[0]+path_end_point[0], -bbox[0,1]-pen_tip[1]+path_end_point[1])

        def space_filling_curve(ele):
            smallest_area = np.inf
            best_angle = 0
            for ra in range(0,90,5):
                ele.rotate(ra)
                bbox = ele.bbox()
                area = (bbox[1,0]-bbox[0,0])*(bbox[1,1]-bbox[0,1])
                if area < smallest_area:
                    best_angle = ra
                    smallest_area = area
                ele.rotate(-ra)
            best_bbox = ele.rotate(best_angle).bbox()
            
            pen_tip_points = []
            number_of_zigzag = 10
            if best_bbox[1,0]-best_bbox[0,0] >= best_bbox[1,1]-best_bbox[0,1]:
                stroke_width = (best_bbox[1,0]-best_bbox[0,0]) / (number_of_zigzag - 1)
                pen_tip_points.append(np.linspace(np.array([best_bbox[0,0], best_bbox[0,1]]), np.array([best_bbox[1,0], best_bbox[0,1]]), number_of_zigzag))
                pen_tip_points.append(np.linspace(np.array([best_bbox[0,0], best_bbox[1,1]]), np.array([best_bbox[1,0], best_bbox[1,1]]), number_of_zigzag))
            else:
                stroke_width = (best_bbox[1,1]-best_bbox[0,1]) / (number_of_zigzag - 1)
                pen_tip_points.append(np.linspace(np.array([best_bbox[0,0], best_bbox[0,1]]), np.array([best_bbox[0,0], best_bbox[1,1]]), number_of_zigzag))
                pen_tip_points.append(np.linspace(np.array([best_bbox[1,0], best_bbox[0,1]]), np.array([best_bbox[1,0], best_bbox[1,1]]), number_of_zigzag))

            pen_tip_line = " ".join([f"L {pen_tip_points[0][i][0]} {pen_tip_points[0][i][1]} L {pen_tip_points[1][i][0]} {pen_tip_points[1][i][1]}" for i in range(len(pen_tip_points[0]))])
            pen_tip_line = "M"+pen_tip_line[1:]
            pen_tip_line = Path(pen_tip_line).rotate(-best_angle).stroke_width(stroke_width).stroke_opacity(0).stroke("white")
            
            r = deepcopy(ele.rotate(-best_angle)).stroke("black").stroke_opacity(1).opacity(1)
            m = Mask(Group(pen_tip_line, r))
            ele.stroke_width(0).mask(m).fill_opacity(1)
            return pen_tip_line

        # keep the original
        original = deepcopy(g[self.pointer])
                
        self.elements = Group(self.elements)

        # self.timeline.add_animation(self.elements, [stroke_opacity(p1=1, p2=0)], 0, 0) # fill(p1=Color(rgb=(0,0,0)), p2=Color(rgb=(0,0,0)))

        if self.is_text:
            for item in self.elements:
                item.stroke_opacity(0)
        else:
            tmp = []
            for item in self.elements:
                tmp.append(item.fill_opacity(0).stroke_opacity(0))
                tmp.append(deepcopy(item))
            self.elements = Group(*tmp[::-1])
        
        g[self.pointer] = Group(*tmp)


        # calculate element drawing durations
        element_durations = [None for _ in range(len(self.elements))]
        if self.is_text:
            for i in range(len(self.elements)):
                element_durations[i] = self.elements[i].border_length()
        else:
            for i in range(0, len(self.elements), 2):
                element_durations[i+1] = self.elements[i+1].border_length()
                if self.elements[i].get_fill() != 'white':
                    element_durations[i] = self.elements[i].border_length()
                else:
                    element_durations[i] = 0

        element_durations = self.get_durations(np.array(element_durations))


        if self.is_text:
            for i in range(0, len(self.elements)):
                self.timeline.add_animation(self.elements[i], [
                        draw([0, 1], [1, 0], 
                        before_update=lambda self: [self.elements.stroke_opacity(1), self.elements.opacity(1)] if self.t==0 else None,
                        after_update = after_update, after_update_kwargs={'element':self.elements[i]})],
                        0,
                        element_durations[i],
                        ease=self.ease)
            
        else:
            
            for i in range(0, len(self.elements), 2):
                self.timeline.add_animation(self.elements[i+1], [
                        draw([0, 1], [1, 0], 
                        before_update=lambda self: self.elements.stroke_opacity(1).fill_opacity(1).opacity(1) if self.t==0 else None,
                        after_update = after_update, after_update_kwargs={'element':self.elements[i+1]})],
                        0,
                        element_durations[i+1],
                        ease=self.ease)
                
                if self.elements[i].get_fill() != 'white':
                    coloring_curve = space_filling_curve(self.elements[i])
                    
                    self.timeline.add_animation(coloring_curve, [
                        draw([0, 1], [1, 0], 
                        before_update=lambda ctx, **kwargs: [ctx.elements.stroke_opacity(1), kwargs['element'].stroke_opacity(1).fill_opacity(1).opacity(1)] if ctx.t==0 else None,
                        before_update_kwargs=dict(element=self.elements[i]),
                        after_update = after_update, after_update_kwargs={'element':coloring_curve})],
                        0,
                        element_durations[i],
                        ease=self.ease)
        
        def place_original(ctx, **kwargs):
            g[kwargs['pointer']] = kwargs['original'].opacity(1)
        self.timeline.add_animation(None, [Tween(before_update=place_original,
                                                 before_update_kwargs=dict(pointer=self.pointer, original=original))], 0, 0)
            
        # self.timeline.add_animation(self.elements, [fill_opacity(1)],
        #                             0,
        #                             self.duration,
        #                             ease=self.ease)

class reveal(Animation):
    def __init__(self, is_elementwise=True, lag_ratio=0.1, mode='rect-lr'):
        super().__init__()
        self.is_elementwise = is_elementwise
        self.lag_ratio = lag_ratio
        assert mode in ['rect-tb', 'rect-bt', 'rect-lr', 'rect-rl', 'arc', 'circle']
        self.mode = mode

    def animation(self):
        masks = []
        elements = []
        def gen_mask(element):
            if 'rect' in self.mode:
                bbox = element.bbox()
                rect = Rectangle(bbox[0,0], bbox[0,1], bbox[1,0]-bbox[0,0], bbox[1,1]-bbox[0,1]).fill('white').opacity(1)        
                if self.mode == 'rect-tb':
                    masks.append(Mask(rect.translate(*(element.anchor_point([0,1])-element.anchor_point([0,0])))))
                elif self.mode == 'rect-bt':
                    masks.append(Mask(rect.translate(*(element.anchor_point([0,0])-element.anchor_point([0,1])))))
                elif self.mode == 'rect-lr':
                    masks.append(Mask(rect.translate(*(element.anchor_point([0,0])-element.anchor_point([1,0])))))
                elif self.mode == 'rect-rl':
                    masks.append(Mask(rect.translate(*(element.anchor_point([1,0])-element.anchor_point([0,0])))))

        if self.is_elementwise:
            for element in self.elements:
                gen_mask(element)
                element.mask(masks[-1])
                elements.append(element)             
        else:
            gen_mask(self.elements)
            [element.mask(masks[-1]) for element in self.elements]
            elements.append(self.elements)
        
        def animate(mask, element, delay):
            if self.mode == 'rect-tb':
                self.timeline.add_animation(mask.elements, [translate(*-(element.anchor_point([0,1])-element.anchor_point([0,0])))], delay, self.duration/len(masks))
            elif self.mode == 'rect-bt':
                self.timeline.add_animation(mask.elements, [translate(*-(element.anchor_point([0,0])-element.anchor_point([0,1])))], delay, self.duration/len(masks))
            elif self.mode == 'rect-lr':
                self.timeline.add_animation(mask.elements, [translate(*-(element.anchor_point([0,0])-element.anchor_point([1,0])))], delay, self.duration/len(masks))
            elif self.mode == 'rect-rl':
                self.timeline.add_animation(mask.elements, [translate(*-(element.anchor_point([1,0])-element.anchor_point([0,0])))], delay, self.duration/len(masks))


        first = True
        for element, mask in zip(elements, masks):
            if first:
                animate(mask, element, 0)
                first = False
            else:
                animate(mask, element, -self.duration/len(masks)*(1-self.lag_ratio))
            

class arrow(Animation):
    def __init__(self, arrow_head):
        super().__init__()
        self.arrow_head = arrow_head

    def animation(self):

        def put_arrow_head(ctx, **elements):
            curve_head = self.elements.point(ctx.et)
            if ctx.t == 1:
                tangent = curve_head - self.elements.point(ctx.et-0.0001)
            else:     
                tangent = self.elements.point(ctx.et+0.0001) - curve_head
            angle = np.rad2deg(np.arctan2(tangent[1], tangent[0]))
            arrow_head = deepcopy(elements['arrow_head'])
            arrow_head.translate(*(curve_head-arrow_head.anchor_point([0.5,0.5]))).rotate(angle)
            g['arrow_head'] = arrow_head

        self.timeline.add_animation(self.elements, [draw(after_update=put_arrow_head, after_update_kwargs=dict(arrow_head=self.arrow_head))], 0, self.duration)


class dim_n_lit(Animation):
    def __init__(self, value=0.3, transition_time=0.2):
        super().__init__()
        self.value = value
        self.transition_time = transition_time

    def animation(self):
        original_opacities = []
        first = True
        for element in self.elements:
            opacity_val = element.get_opacity()
            if opacity_val == 'nil':
                opacity_val = 1
            original_opacities.append(opacity_val)
            if opacity_val > self.value:
                if first:
                    self.timeline.add_animation(element, [opacity(opacity_val, self.value)], 0, self.transition_time)
                    first = False
                else:
                    self.timeline.add_animation(element, [opacity(opacity_val, self.value)], -self.transition_time, self.transition_time)

        self.timeline.add_animation(None, [Tween()], 0, self.duration-2*self.transition_time)

        first = True
        for i, element in enumerate(self.elements):
            if first:
                self.timeline.add_animation(element, [opacity(self.value, original_opacities[i])], 0, self.transition_time)
                first = False
            else:
                self.timeline.add_animation(element, [opacity(self.value, original_opacities[i])], -self.transition_time, self.transition_time)

class draw_and_then_fill(Animation):
    def __init__(self, element_duration=0.25):
        super().__init__()
        self.element_duration = element_duration

    def animation(self):
        total_elements = len(self.elements) if isinstance(self.elements, Group) else 1
        self.duration = (total_elements * self.element_duration) / (1 + 0.075 * total_elements)
        t1 = self.timeline.time()
        
        self.timeline.stagger(self.elements, [draw([0, 1], [1, 0], before_update=lambda self: self.elements.fill_opacity(0) if self.t==0 else None)],
                            0,
                            self.duration,
                            self.duration/4,
                            ease=self.ease)
        self.timeline.add_animation(self.elements, [fill_opacity(1)],
                                    0,
                                    self.duration,
                                    ease=self.ease)


class write(Animation):
    def __init__(self, element_duration=0.25):
        super().__init__()
        self.element_duration = element_duration

    def animation(self):
        total_elements = len(self.elements) if isinstance(self.elements, Group) else 1
        self.duration = (total_elements * self.element_duration) / (1 + 0.075 * total_elements)
        element_duration = 3 * self.duration / (total_elements + 8)
        self.timeline.set([(self.elements.fill_opacity, 0), (self.elements.stroke_opacity, 1)])
        stagger = element_duration / 3

        t1 = self.timeline.time()
        self.timeline.stagger(self.elements, [draw([0, 1], [1, 0])],
                              0,
                              element_duration,
                              stagger,
                              ease=self.ease)
        t2 = self.timeline.time()

        self.timeline.stagger(self.elements, [fill_opacity(1)],
                              t1 - t2 + element_duration,
                              element_duration,
                              stagger,
                              ease=self.ease)
        t3 = self.timeline.time()

        self.timeline.stagger(self.elements, [stroke_opacity(0)],
                              t1 - t3 + 2 * element_duration,
                              element_duration,
                              stagger,
                              ease=self.ease)


class grow(Animation):
    def __init__(self, anchor=[0.5, 0.5, 0.5], from_point=None):
        super().__init__()
        self.anchor = anchor
        self.from_point = from_point

    def animation(self):
        def get_info(elements, anchor, from_point):
            if from_point:
                anchor = elements.anchor(elements, np.array([*anchor, 1.0]))
                from_point = np.array(from_point)
                trans = from_point[:3] - anchor[:3]
                elements.translate(*trans)
                trans = -trans
            else:
                trans = [0, 0, 0]
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info, (self.elements, self.anchor, self.from_point))
        self.timeline.set([(self.elements.scale, (0.001, 0.001, 0.001, self.anchor))])
        self.timeline.add_animation(
            self.elements, [translate(d.x, d.y, d.z),
                            scale(1000, 1000, 1000, self.anchor)],
            0,
            self.duration,
            ease=self.ease)


class shrink(Animation):
    def __init__(self, anchor=[0.5, 0.5, 0.5], to_point=None):
        super().__init__()
        self.anchor = anchor
        self.to_point = to_point

    def animation(self):
        def get_info(elements, anchor, to_point):
            if to_point:
                anchor = elements.anchor(elements, np.array([*anchor, 1.0]))
                to_point = np.array(from_point)
                trans = to_point[:3] - anchor[:3]
            else:
                trans = [0, 0, 0]
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info, (self.elements, self.anchor, self.to_point))
        self.timeline.add_animation(
            self.elements, [translate(d.x, d.y, d.z),
                            scale(0.0001, 0.0001, 0.0001, self.anchor)],
            0,
            self.duration,
            ease=self.ease)


class fade_in(Animation):
    def __init__(self, from_direction=5, from_point=None, from_scale=1):
        super().__init__()
        self.from_direction = from_direction
        self.from_point = from_point
        self.from_scale = from_scale

    def animation(self):
        def get_info(timeline, elements, from_direction, from_point):
            if from_point:
                center = elements.center()
                from_point = np.array(from_point)
                trans = from_point[:3] - center[:3]
            else:
                bbox = elements.bbox()
                width = (bbox[1][0] - bbox[0][0]) / 2
                height = (bbox[1][1] - bbox[0][1]) / 2
                trans = [0, 0, 0] if from_direction == 5\
                    else [0, height, 0] if from_direction == 8\
                    else [0, -height, 0] if from_direction == 2\
                    else [-width, 0, 0] if from_direction == 4\
                    else [width, 0, 0] if from_direction == 6\
                    else [-width, -height, 0] if from_direction == 1\
                    else [width, -height, 0] if from_direction == 3\
                    else [-width, height, 0] if from_direction == 7\
                    else [width, height, 0] if from_direction == 9\
                    else [0, 0, 0]
                trans = np.array(trans)
            elements.translate(*trans)
            trans = -trans
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info,
                           (self.timeline, self.elements, self.from_direction, self.from_point))
        self.timeline.set([(self.elements.opacity, (0)),
                           (self.elements.scale, (self.from_scale, self.from_scale,
                                                  self.from_scale))])
        self.timeline.add_animation(self.elements, [
            translate(d.x, d.y, d.z),
            opacity(1),
            scale(1 / self.from_scale, 1 / self.from_scale, 1 / self.from_scale)
        ],
                                    0,
                                    self.duration,
                                    ease=self.ease)


class fade_out(Animation):
    def __init__(self, to_direction=5, to_point=None, to_scale=1):
        super().__init__()
        self.to_direction = to_direction
        self.to_point = to_point
        self.to_scale = to_scale

    def animation(self):
        def get_info(timeline, elements, to_direction, to_point):
            if to_point:
                center = elements.center()
                to_point = np.array(to_point)
                trans = to_point[:3] - center[:3]
            else:
                bbox = elements.bbox()
                width = (bbox[1][0] - bbox[0][0]) / 2
                height = (bbox[1][1] - bbox[0][1]) / 2
                trans = [0, 0, 0] if to_direction == 5\
                    else [0, height, 0] if to_direction == 8\
                    else [0, -height, 0] if to_direction == 2\
                    else [-width, 0, 0] if to_direction == 4\
                    else [width, 0, 0] if to_direction == 6\
                    else [-width, -height, 0] if to_direction == 1\
                    else [width, -height, 0] if to_direction == 3\
                    else [-width, height, 0] if to_direction == 7\
                    else [width, height, 0] if to_direction == 9\
                    else [0, 0, 0]
                trans = np.array(trans)
            d.x = trans[0]
            d.y = trans[1]
            d.z = trans[2]

        self.timeline.call(get_info,
                           (self.timeline, self.elements, self.to_direction, self.to_point))
        self.timeline.add_animation(self.elements, [
            translate(d.x, d.y, d.z),
            opacity(0),
            scale(self.to_scale, self.to_scale, self.to_scale)
        ],
                                    0,
                                    self.duration,
                                    ease=self.ease)
