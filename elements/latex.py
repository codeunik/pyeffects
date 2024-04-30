import hashlib
import os

import bs4
import numpy as np

from .group import Group
from .path import Path
from .shapes import Rectangle
from .utils import Color

class TexConfig:
    main_font = None
    font_path = None
    mono_font = None
    sans_font = None
    font_size = 40
    fill = "#FFFFFF"
    stroke = "#FFFFFF"
    stroke_width = 1
    page_width = 1920
    page_height = 1080
    line_spacing = 1.2

    # @staticmethod
    # def text_box(width=None, scale_factor=None, margin=None):
    #     TexConfig.margin = round((594.691842 - (width/scale_factor)) / 56.76466 if width and scale_factor \
    #                         else TexConfig.margin if margin is None else margin, 2)
    #     TexConfig.scale_factor = round(width / (594.691842 - margin * 56.76466) if width and margin \
    #                             else TexConfig.scale_factor if scale_factor is None else scale_factor, 2)


def Tex(expr, justify='center'):
    backslash = '\\'
    hash = hashlib.md5(bytes(f"{expr, str(TexConfig.__dict__)}", encoding="utf-8")).hexdigest()
    folder1 = hash[:3]
    folder2 = hash[3:6]
    folder3 = hash[6:]
    if not os.path.exists(f"/tmp/pyeffects/text/{folder1}/{folder2}/{folder3}/texput.svg"):
        s = f'''\\documentclass[11pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
\\usepackage{{tikz}}
\\usepackage[none]{{hyphenat}}
\\usepackage[a4paper, margin=0pt,paperheight={TexConfig.page_height}bp,paperwidth={TexConfig.page_width}bp]{{geometry}}
\\usepackage{{fontspec}}
\\defaultfontfeatures{{Ligatures={{NoCommon, NoDiscretionary, NoHistoric, NoRequired, NoContextual}}}}
''' + (f"\\setmainfont{'[Path='+TexConfig.font_path+']' if TexConfig.font_path else ''}{{{TexConfig.main_font}}}" if TexConfig.main_font else "") \
    + (f"\\setmonofont{{{TexConfig.mono_font}}}" if TexConfig.mono_font else "") \
    + (f"\\setsansfont{{{TexConfig.sans_font}}}" if TexConfig.sans_font else "") \
    + f'''\\parindent=0pt
\\thispagestyle{{empty}}
\\linespread{{{TexConfig.line_spacing}}}

\\begin{{document}}
{'{}begin{{center}}'.format(backslash) if justify=='center' else ''}
{{\\fontsize{{{TexConfig.font_size}}}{{{1.2*TexConfig.font_size}}}\selectfont {expr}}}
{'{}end{{center}}'.format(backslash) if justify=='center' else ''}
\\end{{document}}'''

        os.system(f'''mkdir -p /tmp/pyeffects/text/{folder1}/{folder2}/{folder3} && cd /tmp/pyeffects/text/{folder1}/{folder2}/{folder3} && xelatex -interaction=nonstopmode -halt-on-error -no-pdf $(cat << 'EOF'
{s}
EOF
) > /dev/null 2>&1 && dvisvgm -e -n texput.xdv > /dev/null 2>&1''')
    
    with open(f'/tmp/pyeffects/text/{folder1}/{folder2}/{folder3}/texput.svg', 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    uses = soup.find_all('use')
    rects = soup.find_all('rect')

    chars = Group()
    if uses:
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
    # chars.scale(TexConfig.scale_factor, TexConfig.scale_factor)
    if len(chars):
        return chars
    else:
        chars.add(Path("M0,0"))
        return chars
