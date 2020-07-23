import os

import bs4

from .. import config
from .element import Element
from .path import Path


def text():
    pass


class Text(Element):
    attrs = [
        "x", "y", "text", "font_family", "font_style", "font_weight",
        "font_variant", "font_stretch", "font_size", "font_size_adjust",
        "letter_spacing", "word_spacing", "text_decoration", "text_anchor"
    ]

    def __init__(self,
                 text,
                 x=0,
                 y=0,
                 font_family=None,
                 font_style=None,
                 font_weight=None,
                 font_variant=None,
                 font_stretch=None,
                 font_size=None,
                 font_size_adjust=None,
                 letter_spacing=None,
                 word_spacing=None,
                 text_decoration=None,
                 text_anchor=None,
                 defs="",
                 **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.text = text
        self.font_family = font_family
        self.font_style = font_style
        self.font_weight = font_weight
        self.font_variant = font_variant
        self.font_stretch = font_stretch
        self.font_size = font_size
        self.font_size_adjust = font_size_adjust
        self.letter_spacing = letter_spacing
        self.word_spacing = word_spacing
        self.text_decoration = text_decoration
        self.text_anchor = text_anchor
        self.defs = defs

    def update(self,
               x=None,
               y=None,
               text=None,
               font_family=None,
               font_style=None,
               font_weight=None,
               font_variant=None,
               font_stretch=None,
               font_size=None,
               font_size_adjust=None,
               letter_spacing=None,
               word_spacing=None,
               text_decoration=None,
               text_anchor=None,
               defs=None,
               **kwargs):
        loc = locals().copy()
        for attr, value in loc.items():
            if attr in Text.attrs and value is not None:
                setattr(self, attr, value)
        if defs is not None:
            self.defs += defs

        super().update(**kwargs)

    def draw(self):
        s = f"{self.defs}<text "
        for prop in [
                'x', 'y', 'font_family', 'font_style', 'font_weight',
                'font_variant', 'font_stretch', 'font_size',
                'font_size_adjust', 'letter_spacing', 'word_spacing',
                'text_decoration'
        ]:
            if getattr(self, prop) is not None:
                s += f'{prop.replace("_","-")}="{getattr(self, prop)}" '
        s += super().draw()
        if self.text:
            s += f">{self.text}</text>"
        else:
            s += "></text>"
        return s

    def to_paths(self):
        os.system("mkdir -p tmp")
        with open("tmp/txt.svg", 'w') as f:
            f.write(
                f'''<svg width="{config.WIDTH}" height="{config.HEIGHT}" viewBox="{config.VIEWBOX_X} {config.VIEWBOX_Y} {config.VIEWBOX_WIDTH} {config.VIEWBOX_HEIGHT}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"> '''
                + self.svg_str() + '</svg>')

        os.system(
            "cd tmp/ && inkscape txt.svg --export-text-to-path --export-plain-svg=path.svg"
        )
        with open("tmp/path.svg", 'r') as f:
            soup = bs4.BeautifulSoup(f, "xml")

        def transform_text_point(point):
            return complex(point.real, -point.imag)

        paths = soup.find_all('path')
        text_path = Path("")

        for path in paths:
            path = Path(path['d'], **self.__dict__)
            path.transform_path(transform_text_point)
            text_path.path.append(path.path)

        bbox = text_path.bbox()
        text_path.update(
            translate=[-(bbox[0] + bbox[1]) / 2, -(bbox[2] + bbox[3]) / 2])
        return text_path
