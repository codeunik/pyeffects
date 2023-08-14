__author__ = "Partha Ghosh (patha31415@gmail.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2020 Partha Ghosh"
__license__ = "MIT"

global g, b # global container, blocked elements container

class G(dict):

    def __init__(self):
        super().__init__()
    
    def get(self, *pointers):
        x = self
        for pointer in pointers:
            x = x[pointer]
        return x

    def set(self, *pointers, value):
        x = self
        for i, pointer in enumerate(pointers):
            x.setdefault(pointer, dict())
            if i == len(pointers)-1:
                x[pointer] = value
            else:
                x = x[pointer]

b = dict()
g = G()

import warnings

from .animation import *
from .constants import *
from .elements import *
from .render import Renderer
from .timeline import Timeline
from .tween import *

warnings.filterwarnings("ignore")

import os
os.system("mkdir -p /tmp/pyeffects/text")