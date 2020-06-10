from .agent import Agent, Keymap
from .body_parts.parts import BodyBase, Head
from flatland.utils.config import ActionTypes, KeyTypes
from pygame.locals import *
import math

class BaseAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = BodyBase(can_eat=True, can_grasp=True, can_activate=True, radius=15)

        super(BaseAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)


    @property
    def key_mapping(self):

        keys = []

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append( Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1 ) )

        return keys


class HeadAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = BodyBase(can_eat=True, can_grasp=True, can_activate=True, radius=15)

        super(HeadAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range = math.pi)

        self.add_body_part(self.head)


    @property
    def key_mapping(self):

        keys = []

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        return keys
