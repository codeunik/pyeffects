__author__ = "Partha Ghosh (patha31415@gmail.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2020 Partha Ghosh"
__license__ = "MIT"


global g # global container, blocked elements container

class G(dict):

    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        try:
            value.name = key
        except:
            pass
        # if isinstance(self[key], Group):
        #     for element in self[key]:
        #         if not hasattr(element, 'name'):
        #             self.__setitem__(uuid.uuid4().hex, element)

    def asynk(self, key):
        async def f(key):
            return super(G, self).__getitem__(key)
        return f(key)

    def __delitem__(self, key):
        # if isinstance(self[key], Group):
        #     for element in self[key]:
        #         super().__delitem__(element.name)
        super().__delitem__(key)


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