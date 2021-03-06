import hashlib
import os

import bs4
import numpy as np

from .group import Group
from .path import Path
from .shapes import Rectangle


class TexConfig:
    main_font = None
    mono_font = None
    sans_font = None
    margin = 5.5
    scale_factor = 8
    fill = [255, 255, 255]
    stroke = [255, 255, 255]
    stroke_width = 1

    @staticmethod
    def text_box(width=None, scale_factor=None, margin=None):
        TexConfig.margin = round((594.691842 - (width/scale_factor)) / 56.76466 if width and scale_factor \
                            else TexConfig.margin if margin is None else margin, 2)
        TexConfig.scale_factor = round(width / (594.691842 - margin * 56.76466) if width and margin \
                                else TexConfig.scale_factor if scale_factor is None else scale_factor, 2)


def Tex(expr):
    filename = hashlib.md5(bytes(f"{expr, TexConfig.main_font, TexConfig.mono_font, TexConfig.sans_font, TexConfig.margin}", encoding="utf-8")).hexdigest()
    if not os.path.exists(f"/tmp/{filename}.tex"):
        with open(f'/tmp/{filename}.tex', 'w') as f:
            f.write(f'''
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
\\usepackage{{tikz}}
\\usepackage[none]{{hyphenat}}
\\usepackage[a4paper, margin={TexConfig.margin}cm]{{geometry}}
\\usepackage{{fontspec}}
''' + (f"\\setmainfont{{{TexConfig.main_font}}}" if TexConfig.main_font else "")
    + (f"\\setmonofont{{{TexConfig.mono_font}}}" if TexConfig.mono_font else "")
    + (f"\\setsansfont{{{TexConfig.sans_font}}}" if TexConfig.sans_font else "")
+ f'''\\thispagestyle{{empty}}
\\begin{{document}}
{expr}
\\end{{document}}''')

        os.system(f"cd /tmp && xelatex -no-pdf {filename}.tex > /dev/null 2>&1 && dvisvgm -e -n {filename}.xdv > /dev/null 2>&1")

    with open(f'/tmp/{filename}.svg', 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    uses = soup.find_all('use')
    rects = soup.find_all('rect')

    def transform_tex_point(point, x, y):
        return complex(point.real + x, -point.imag - y)

    chars = Group()
    fx = float(uses[0].attrs['x'])
    fy = float(uses[0].attrs['y'])
    for use in uses:
        path = soup.find(id=use.attrs['xlink:href'][1:]).attrs['d']
        x = float(use.attrs['x']) - fx
        y = float(use.attrs['y']) - fy
        path = Path(path)
        path.matrix(np.array([[1, 0, 0, x], [0, -1, 0, -y], [0, 0, 1, 0], [0, 0, 0, 1.0]]))
        chars.add(path)
    for rect in rects:
        x = float(rect.attrs['x']) - fx
        y = float(rect.attrs['y']) - fy
        width = float(rect.attrs['width'])
        height = float(rect.attrs['height'])
        r = Rectangle(0, 0, width, height)
        r.matrix(np.array([[1, 0, 0, x], [0, -1, 0, -y], [0, 0, 1, 0], [0, 0, 0, 1.0]]))
        chars.add(r)

    chars.fill(TexConfig.fill).stroke(TexConfig.stroke).stroke_width(TexConfig.stroke_width)
    chars.scale(TexConfig.scale_factor, TexConfig.scale_factor)
    return chars
