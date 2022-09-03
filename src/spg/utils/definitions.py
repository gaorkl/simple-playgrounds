""" This module lists all the definitions.
"""

# pylint: disable=missing-class-docstring
from collections import namedtuple
from enum import IntEnum, auto

SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9
LINEAR_FORCE = 100
ANGULAR_VELOCITY = 0.3
ARM_MAX_FORCE = 500
MAX_GRASP_FORCE = 600

WALL_DEPTH = 10

PYMUNK_STEPS = 10

VISIBLE_ALPHA = 255
INVISIBLE_ALPHA = 75
DEFAULT_INTERACTION_RANGE = 5


class PymunkCollisionCategories(IntEnum):

    # Must start at one:
    TRAVERSABLE = auto()
    TRANSPARENT = auto()
    SENSOR = auto()
    SENSOR_CONTACT = auto()
    INTERACTION = auto()
    BOUNDARY = auto()
    NO_TEAM = auto()


class KeyTypes(IntEnum):

    PRESS_HOLD = auto()
    PRESS_ONCE = auto()


FRICTION_ENTITY = 0.8
ELASTICITY_ENTITY = 0.5


class CollisionTypes(IntEnum):

    ELEMENT = auto()

    PART = auto()
    CONTACT = auto()
    ACTIVABLE = auto()
    GEM = auto()
    GRASPABLE = auto()
    ACTIVABLE_BY_GEM = auto()
    TELEPORT = auto()

    DEVICE = auto()
    MODIFIER = auto()

    GRASPER = auto()
    ACTIVATOR = auto()

    # ACTIVE_INTERACTOR interacts only with PASSIVE_INTERACTOR
    # PASSIVE_INTERACTOR interacts with ACTIVE OR PASSIVE
    ACTIVE_INTERACTOR = auto()
    PASSIVE_INTERACTOR = auto()


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
    extended_enum = IntEnum("CollisionTypes", names)

    return extended_enum


class ElementTypes(IntEnum):

    # Basic Entities
    BASIC = auto()
    DOOR = auto()
    WALL = auto()
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
    # PASSIVE_INTERACTOR interacts with ACTIVE OR PASSIVE
    KEY = auto()

    # Interactive
    REWARD_ON_ACTIVATION = auto()
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
    BEAM = auto()
    BEAM_HOMING = auto()
    PORTAL = auto()

    # Modifier Zones
    SENSOR_DISABLER = auto()
    COMM_DISABLER = auto()
    ACTUATOR_DISABLER = auto()

    SPAWNER = auto()


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
    TOPDOWN_LOCAL = auto()
    TOPDOWN_GLOBAL = auto()
    PERFECT_SEMANTIC = auto()


Detection = namedtuple("Detection", "entity, distance, angle")
