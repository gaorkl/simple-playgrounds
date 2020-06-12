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

    GRASP = 6
    EAT = 7
    ACTIVATE = 8

class KeyTypes(IntEnum):

    PRESS_HOLD = 1
    PRESS_RELEASE = 2


geometric_shapes = {'line': 2, 'circle': 60, 'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6}
