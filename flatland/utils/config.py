from enum import IntEnum, Enum

SIMULATION_STEPS = 4
SPACE_DAMPING = 0.9


class CollisionTypes(IntEnum):

    AGENT = 1
    CONTACT = 2
    INTERACTIVE = 3
    ZONE = 4
    GEM = 5


class ControllerTypes(Enum):

    KEYBOARD = 1
    RANDOM = 2
    EXTERNAL = 3


class ActionTypes(IntEnum):

    DISCRETE = 1
    CONTINUOUS = 2

    LONGITUDINAL_VELOCITY = 3
    LATERAL_VELOCITY = 4
    ANGULAR_VELOCITY = 5

    PRESS_HOLD = 6
    PRESS_RELEASE = 7

    GRASP = 8
    EAT = 9
    ACTIVATE = 10


geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6}
