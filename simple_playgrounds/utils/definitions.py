""" This module lists all the definitions.
"""

from enum import IntEnum, Enum, auto
from collections import namedtuple

# pylint: disable=missing-class-docstring

SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9
LINEAR_FORCE = 100
ANGULAR_VELOCITY = 0.3
ARM_MAX_FORCE = 500


class AgentPartTypes(IntEnum):

    PART = auto()
    HEAD = auto()
    EYE = auto()
    ARM = auto()
    HAND = auto()
    PLATFORM = auto()


class SceneElementTypes(IntEnum):

    # Basic Entities
    BASIC = auto()
    DOOR = auto()
    COLOR_CHANGING = auto()

    # Contact entities
    VISIBLE_ENDGOAL = auto()
    VISIBLE_DEATHTRAP = auto()
    CANDY = auto()
    POISON = auto()
    SWITCH = ()

    # Edibles
    APPLE = auto()
    ROTTEN_APPLE = auto()

    # Gems
    COIN = auto()
    KEY = auto()

    # Interactive
    LEVER = auto()
    DISPENSER = auto()
    CHEST = auto()
    VENDING_MACHINE = auto()
    LOCK = auto()

    # Zone
    GOAL_ZONE = auto()
    DEATH_ZONE = auto()
    TOXIC_ZONE = auto()
    HEALING_ZONE = auto()

    # Proximity
    FAIRY = auto()
    FIREBALL = auto()

    # Teleport
    TELEPORT = auto()

    FIELD = auto()


class SensorTypes(IntEnum):

    SENSOR = auto()
    VISUAL = auto()
    SEMANTIC = auto()
    ROBOTIC = auto()

    RGB = auto()
    GREY = auto()
    LIDAR = auto()
    TOUCH = auto()
    Proximity = auto()

    SEMANTIC_CONE = auto()
    SEMANTIC_RAY = auto()
    TOP_DOWN = auto()
    FULL_PLAYGROUND = auto()


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

    Examples:
        CustomCollisionTypes = add_custom_collision(CollisionTypes, JELLY)

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


class ActionSpaces(IntEnum):

    DISCRETE = auto()
    CONTINUOUS = auto()


class KeyTypes(IntEnum):

    PRESS_HOLD = auto()
    PRESS_ONCE = auto()


Detection = namedtuple('Detection', 'entity, distance, angle')

geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3,
                    'square': 4, 'pentagon': 5, 'hexagon': 6}
