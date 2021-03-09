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

    AGENT = auto()
    CONTACT = auto()
    INTERACTIVE = auto()
    PASSIVE = auto()
    GEM = auto()
    EDIBLE = auto()
    GRASPABLE = auto()
    ACTIVATED_BY_GEM = auto()
    TELEPORT = auto()


def add_custom_collision(collision_types, name):
    """
    Function that allows to add new collisions to CollisionTypes.
    This is used when an user wants to create a new type of Entity,
    that requires particular collision handler and behavior.

    Args:
        collision_types: CollisionTypes enum.
            Either the default one or a custom one.
        name: name of the new collision type (UPPERCASE)

    Returns:
        New CollisionTypes Enum.

    """

    names = [m.name for m in collision_types] + [name]
    extended_enum = IntEnum('CollisionTypes', names)

    return extended_enum


class ControllerTypes(Enum):

    KEYBOARD = 1
    RANDOM = 2
    EXTERNAL = 3


class ActionTypes(IntEnum):

    DISCRETE = auto()
    CONTINUOUS_CENTERED = auto()
    CONTINUOUS_NOT_CENTERED = auto()

    LONGITUDINAL_FORCE = auto()
    LATERAL_FORCE = auto()
    ANGULAR_VELOCITY = auto()

    GRASP = auto()
    EAT = auto()
    ACTIVATE = auto()


class KeyTypes(IntEnum):

    PRESS_HOLD = 1
    PRESS_ONCE = 2


class SensorModality(Enum):
    VISUAL = auto()
    SEMANTIC = auto()
    ROBOTIC = auto()
    UNDEFINED = auto()


Detection = namedtuple('Detection', 'entity, distance, angle')

geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3,
                    'square': 4, 'pentagon': 5, 'hexagon': 6}
