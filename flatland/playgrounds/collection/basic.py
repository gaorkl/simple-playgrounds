import pymunk, pygame
import pymunk.pygame_util
from pygame.color import THECOLORS

from flatland import scenes as  scenes
from flatland.entities import basic, yielder, actionable
from flatland.utils.config import *

from flatland.playgrounds.playground import PlaygroundGenerator, Playground

from flatland.default_parameters.scenes import *

import random


@PlaygroundGenerator.register_subclass('basic')
class Basic(Playground):

    def __init__(self, params ):

        super(Basic, self).__init__(params)
