import os

import numpy as np

import bs4

from .group import Group
from .path import Path


class TexConfig:
    main_font = None
    mono_font = None
    sans_font = None
    margin = 5.5


def use_fonts():
    return (f"\\setmainfont{{{TexConfig.main_font}}}"
            if TexConfig.main_font else "")
    +(f"\\setmonofont{{{TexConfig.mono_font}}}" if TexConfig.mono_font else "")
    +(f"\\setsansfont{{{TexConfig.sans_font}}}" if TexConfig.sans_font else "")


def Tex(expr):
    with open('/tmp/text.tex', 'w') as f:
        f.write(f'''
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
\\usepackage[a4paper, margin={TexConfig.margin}cm]{{geometry}}
\\usepackage{{fontspec}}
''' + use_fonts() + f'''
\\thispagestyle{{empty}}
\\begin{{document}}
{expr}
\\end{{document}}''')

    os.system("cd /tmp && xelatex -no-pdf text.tex && dvisvgm -e -n text.xdv")

    with open('/tmp/text.svg', 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    uses = soup.find_all('use')

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
        path.apply_matrix(np.array([[1, 0, x], [0, -1, -y], [0, 0, 1]]))
        chars.append(path)

    # if merge:
    #     tex = Path("")
    #     for char in chars:
    #         tex.append(char.path)
    #     tex.place_at_pos(0, 0)
    #     tex.update(stroke_width=stroke_width)
    #     tex.scale(scale)
    #     return tex
    # else:
    chars.fill([0, 0, 0])
    chars.scale(8, 8)
    chars.place_at_pos(0.5, 0.5)
    for i in range(len(chars)):
        chars[i] = chars[i].abs_transform()
    return chars
