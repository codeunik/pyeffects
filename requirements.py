import os

modules = [
    'numpy',
    'beautifulsoup4',
    'lxml',
    'svgpathtools',
    'pandas',
    'opencv-python',
    'tqdm'
]

os.system(f'pip install {" ".join(modules)}')