"""
Module defining standard agents
"""
import math

import pymunk
from pygame.locals import *

from simple_playgrounds.entities.agents.agent import Agent
from simple_playgrounds.entities.agents.parts import Head, Hand, HolonomicPlatform, Eye, Arm, FixedPlatform
from simple_playgrounds.utils import Keymap
from simple_playgrounds.utils.definitions import ActionTypes, KeyTypes

#pylint: disable=line-too-long
#pylint: disable=undefined-variable
#pylint: disable=abstract-class-instantiated

class BaseAgent(Agent):
    """
    Base Agent with a single HolonomicPlatform as a Base.
    No interactive actions.
    """
    def __init__(self, initial_position=None, controller = None, **kwargs):

        base_agent = HolonomicPlatform(name='base', radius=10,
                                       can_eat=False, can_grasp=False, can_activate=False, can_absorb=False)

        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        # Assign controller once all body parts are declared
        self.controller = controller

    @property
    def key_mapping(self):
        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        return keys


class BaseInteractiveAgent(Agent):
    """
        Base Agent with a single HolonomicPlatform as a Base.
        With Interactive actions.
        """

    def __init__(self, initial_position=None, controller = None, **kwargs):
        base_agent = HolonomicPlatform(name='base', radius=10,
                                       can_eat=True, can_grasp=True, can_activate=True, can_absorb=True)

        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        # Assign controller once all body parts are declared
        self.controller = controller

    @property
    def key_mapping(self):
        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        return keys


class HeadEyeAgent(Agent):
    """
    Holonomic Platform with a Head, and Two eyes attached to the head.

    Attributes:
        head: Head of the agent
        eye_l: Left Eye
        eye_r: Right Eye
    """

    def __init__(self, initial_position=None, controller = None,**kwargs):

        base_agent = HolonomicPlatform(can_eat=True, can_grasp=True, can_activate=True, can_absorb=True)

        super(HeadEyeAgent, self).__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range=math.pi, name='head')
        self.add_body_part(self.head)

        self.eye_l = Eye(self.head, [-8, 8], angle_offset=math.pi/4, rotation_range=math.pi, name='left_eye')
        self.add_body_part(self.eye_l)

        self.eye_r = Eye(self.head, [8, 8], angle_offset=-math.pi/4, rotation_range=math.pi, name='rigth_eye')
        self.add_body_part(self.eye_r)

        # Assign controller once all body parts are declared
        self.controller = controller


    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.eye_l.name, ActionTypes.ANGULAR_VELOCITY, K_h, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.eye_l.name, ActionTypes.ANGULAR_VELOCITY, K_j, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.eye_r.name, ActionTypes.ANGULAR_VELOCITY, K_k, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.eye_r.name, ActionTypes.ANGULAR_VELOCITY, K_l, KeyTypes.PRESS_HOLD, 1))

        return keys


class HeadAgent(Agent):

    """
    Agent with a Head.

    Attributes:
        head: Head of the agent
    """

    def __init__(self, initial_position=None,controller = None, **kwargs):

        base_agent = HolonomicPlatform(can_eat=True, can_grasp=True, can_activate=True, can_absorb=True, radius=15)
        super(HeadAgent, self).__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range=math.pi, radius=10, name='head')
        self.add_body_part(self.head)

        # Assign controller once all body parts are declared
        self.controller = controller

    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.GRASP, K_g, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ACTIVATE, K_a, KeyTypes.PRESS_RELEASE, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.EAT, K_e, KeyTypes.PRESS_RELEASE, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LATERAL_FORCE, K_c, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LATERAL_FORCE, K_v, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_n, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_m, KeyTypes.PRESS_HOLD, 1))

        return keys


class TurretAgent(Agent):

    """
    Agent with a Head.
    Base is fixed.

    Attributes:
        head: Head of the agent
    """

    def __init__(self, initial_position=None, controller = None,**kwargs):

        base_agent = FixedPlatform(radius=15)
        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range=math.pi, radius=10, name='head')
        self.add_body_part(self.head)

        # Assign controller once all body parts are declared
        self.controller = controller


    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.head.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, 1))

        return keys


class ArmAgent(Agent):
    """
        Agent with two Arms.

        Attributes:
            head: Head of the agent
            arm_l: left arm
            arm_l_2: second segment of left arm
            arm_r: right arm
            arm_r_2: second segment of right arm
        """
    def __init__(self, initial_position=None,controller = None, **kwargs):

        base_agent = HolonomicPlatform(can_eat=True, can_grasp=True, can_activate=True, can_absorb=True, radius=15)

        super(ArmAgent, self).__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.base_platform.shape_filter = pymunk.ShapeFilter(group=1)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range=math.pi, radius=10)
        self.add_body_part(self.head)

        self.arm_r = Arm(base_agent, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.arm_l = Arm(base_agent, [-15, 0], angle_offset=math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_l)

        self.arm_l_2 = Arm(self.arm_l, self.arm_l.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_l_2)

        # Assign controller once all body parts are declared
        self.controller = controller

    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

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
    """
        Agent with an Arm and a Hand attached to this arm.

        Attributes:
            arm_r: right arm
            arm_r_2: second segment of right arm
            hand_r: hand attached to arm_r_2
        """
    def __init__(self, initial_position=None,controller = None, **kwargs):

        base_agent = HolonomicPlatform(radius=15)

        super(ArmHandAgent, self).__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.base_platform.shape_filter = pymunk.ShapeFilter(group=1)

        self.arm_r = Arm(base_agent, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.hand_r = Hand(self.arm_r_2, self.arm_r_2.extremity_anchor_point, radius=8, rotation_range=math.pi)
        self.add_body_part(self.hand_r)

        # Assign controller once all body parts are declared
        self.controller = controller

    @property
    def key_mapping(self):

        keys = []

        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_RIGHT, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.ANGULAR_VELOCITY, K_LEFT, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_UP, KeyTypes.PRESS_HOLD, 1))
        keys.append(Keymap(self.base_platform.name, ActionTypes.LONGITUDINAL_FORCE, K_DOWN, KeyTypes.PRESS_HOLD, -1))

        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_v, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r.name, ActionTypes.ANGULAR_VELOCITY, K_b, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_x, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.arm_r_2.name, ActionTypes.ANGULAR_VELOCITY, K_c, KeyTypes.PRESS_HOLD, 1))

        keys.append(Keymap(self.hand_r.name, ActionTypes.ANGULAR_VELOCITY, K_g, KeyTypes.PRESS_HOLD, -1))
        keys.append(Keymap(self.hand_r.name, ActionTypes.ANGULAR_VELOCITY, K_f, KeyTypes.PRESS_HOLD, 1))

        return keys
