from .agent import Agent
from flatland.utils.config import  Keymap
from .body_parts.parts import *
from flatland.utils.config import ActionTypes, KeyTypes
from pygame.locals import *
import math
import pymunk


class BaseAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = Platform(name ='base', can_eat=True, can_grasp=True, can_activate=True, can_absorb = True, radius = 10)

        super(BaseAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)


    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append( Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1 ) )

        return keys


class HeadEyeAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = Platform(can_eat=True, can_grasp=True, can_activate=True, can_absorb = True)

        super(HeadEyeAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range = math.pi, name = 'head')
        self.add_body_part(self.head)

        self.eye_l = Eye(self.head, [-8, 8], angle_offset=math.pi/4, rotation_range=math.pi, name = 'left_eye')
        self.add_body_part(self.eye_l)

        self.eye_r = Eye(self.head, [8, 8], angle_offset=-math.pi/4, rotation_range=math.pi, name = 'rigth_eye')
        self.add_body_part(self.eye_r)


    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.eye_l.name, ActionTypes.ANGULAR_VELOCITY, K_h, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.eye_l.name, ActionTypes.ANGULAR_VELOCITY, K_j, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.eye_r.name, ActionTypes.ANGULAR_VELOCITY, K_k, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.eye_r.name, ActionTypes.ANGULAR_VELOCITY, K_l, KeyTypes.PRESS_HOLD, 1))

        return keys

class HeadAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = HolonomicPlatform(can_eat=True, can_grasp=True, can_activate=True, can_absorb = True, radius=15)
        super(HeadAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range = math.pi, radius=10, name = 'head')
        self.add_body_part(self.head)


    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))


        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        return keys


class ArmAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = Platform(can_eat=True, can_grasp=True, can_activate=True, can_absorb = True, radius=15)

        super(ArmAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)

        self.base.shape_filter = pymunk.ShapeFilter(group=1)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range = math.pi, radius = 10)
        self.add_body_part(self.head)

        self.arm_r = Arm(base_agent, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.arm_l = Arm(base_agent, [-15, 0], angle_offset=math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_l)

        self.arm_l_2 = Arm(self.arm_l, self.arm_l.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_l_2)

    @property
    def key_mapping(self):

        keys = []

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_v, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_b, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_x, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_c, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_l.name, ActionTypes.ANGULAR_VELOCITY, K_g, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_l.name, ActionTypes.ANGULAR_VELOCITY, K_f, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_l_2.name, ActionTypes.ANGULAR_VELOCITY, K_d, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_l_2.name, ActionTypes.ANGULAR_VELOCITY, K_s, KeyTypes.PRESS_HOLD, 1))

        return keys


class ArmHandAgent(Agent):

    def __init__(self, initial_position, **kwargs):

        base_agent = Platform(radius=15)

        super(ArmHandAgent, self).__init__(initial_position=initial_position, base=base_agent, **kwargs)

        self.base.shape_filter = pymunk.ShapeFilter(group=1)

        self.arm_r = Arm(base_agent, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.hand_r = Hand(self.arm_r_2, self.arm_r_2.extremity_anchor_point, radius=8, rotation_range=math.pi)
        self.add_body_part(self.hand_r)


    @property
    def key_mapping(self):

        keys = []

        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1 ) )
        keys.append( Keymap(self.base.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1 ) )

        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base.name, ActionTypes.LONGITUDINAL_VELOCITY, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_v, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_b, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_x, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_c, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.hand_r.name, ActionTypes.ANGULAR_VELOCITY, K_g, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.hand_r.name, ActionTypes.ANGULAR_VELOCITY, K_f, KeyTypes.PRESS_HOLD, 1))

        return keys

