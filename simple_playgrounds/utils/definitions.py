"""
Default definitions
"""

from enum import IntEnum, Enum, auto
from collections import namedtuple

#pylint: disable=missing-class-docstring

SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9


class SceneElementTypes(Enum):

    FIELD = 'field'
    DISPENSER = 'dispenser'


class CollisionTypes(IntEnum):

    AGENT = 1
    CONTACT = 2
    INTERACTIVE = 3
    PASSIVE = 4
    GEM = 5
    EDIBLE = 6
    GRASPABLE = 7
    ACTIVATED_BY_GEM = 8


class ControllerTypes(Enum):

    KEYBOARD = 1
    RANDOM = 2
    EXTERNAL = 3


class ActionTypes(IntEnum):

    DISCRETE = 1
    CONTINUOUS = 2

    LONGITUDINAL_FORCE = 3
    LATERAL_FORCE = 4
    ANGULAR_VELOCITY = 5

    GRASP = 6
    EAT = 7
    ACTIVATE = 8


class SensorTypes(IntEnum):

    RGB = 1


class KeyTypes(IntEnum):

    PRESS_HOLD = 1
    PRESS_RELEASE = 2


class SensorModality(Enum):
    VISUAL = auto()
    GEOMETRIC = auto()
    SEMANTIC = auto()
    UNDEFINED = auto()


Action = namedtuple('Action', 'body_part action action_type min max')

Keymap = namedtuple('KeyMap', 'body_part action key key_behavior key_value')

LidarPoint = namedtuple('Point', 'entity distance angle')

geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3,
                    'square': 4, 'pentagon': 5, 'hexagon': 6}
