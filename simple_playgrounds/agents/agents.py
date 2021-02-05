"""
Module defining standard agents
"""
import math

import pymunk
from pygame.locals import *

from simple_playgrounds.agent import Agent
from .parts import Head, Hand, HolonomicPlatform, Eye, Arm, FixedPlatform, ForwardPlatform
from simple_playgrounds.utils.definitions import KeyTypes

# pylint: disable=too-few-public-methods
# pylint: disable=line-too-long
# pylint: disable=undefined-variable
# pylint: disable=abstract-class-instantiated


class BaseAgent(Agent):
    """
    Base Agent with a single HolonomicPlatform as a Base.
    No interactive actions.
    """
    def __init__(self, initial_position=None, controller=None, **kwargs):

        base_agent = ForwardPlatform(name='base',
                                     can_eat=False, can_grasp=False, can_activate=False, can_absorb=False)

        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.base_platform.longitudinal_force_actuator.assign_key(K_UP, KeyTypes.PRESS_HOLD, 1)
        self.base_platform.longitudinal_force_actuator.assign_key(K_DOWN, KeyTypes.PRESS_HOLD, -1)

        self.base_platform.angular_velocity_actuator.assign_key(K_RIGHT, KeyTypes.PRESS_HOLD, 1)
        self.base_platform.angular_velocity_actuator.assign_key(K_LEFT, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class BaseInteractiveAgent(Agent):
    """
        Base Agent with a single HolonomicPlatform as a Base.
        With Interactive actions.
        """

    def __init__(self, initial_position=None, controller=None, **kwargs):
        base_agent = ForwardPlatform(name='base', radius=15,
                                     can_eat=True, can_grasp=True, can_activate=True, can_absorb=True)

        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.base_platform.longitudinal_force_actuator.assign_key(K_UP, KeyTypes.PRESS_HOLD, 1)
        self.base_platform.longitudinal_force_actuator.assign_key(K_DOWN, KeyTypes.PRESS_HOLD, -1)

        self.base_platform.angular_velocity_actuator.assign_key(K_RIGHT, KeyTypes.PRESS_HOLD, 1)
        self.base_platform.angular_velocity_actuator.assign_key(K_LEFT, KeyTypes.PRESS_HOLD, -1)

        self.base_platform.grasp_actuator.assign_key(K_g, KeyTypes.PRESS_HOLD, 1)
        self.base_platform.activate_actuator.assign_key(K_a, KeyTypes.PRESS_ONCE, 1)
        self.base_platform.eat_actuator.assign_key(K_e, KeyTypes.PRESS_ONCE, 1)

        # Assign controller once all body parts are declared
        self.controller = controller


class HeadAgent(BaseInteractiveAgent):
    """
    Holonomic Platform with a Head, and Two eyes attached to the head.

    Attributes:
        head: Head of the agent
        eye_l: Left Eye
        eye_r: Right Eye
    """

    def __init__(self, initial_position=None, controller=None, **kwargs):

        super().__init__(initial_position=initial_position, controller=controller, **kwargs)

        self.head = Head(self.base_platform, [0, 0], radius=10, angle_offset=0, rotation_range=math.pi, name='head')
        self.add_body_part(self.head)

        # New Key maps
        self.head.angular_velocity_actuator.assign_key(K_n, KeyTypes.PRESS_HOLD, -1)
        self.head.angular_velocity_actuator.assign_key(K_m, KeyTypes.PRESS_HOLD, 1)

        # Assign controller once all body parts are declared
        self.controller = controller


class HeadEyeAgent(HeadAgent):
    """
    Holonomic Platform with a Head, and Two eyes attached to the head.

    Attributes:
        head: Head of the agent
        eye_l: Left Eye
        eye_r: Right Eye
    """

    def __init__(self, initial_position=None, controller=None, **kwargs):
        super().__init__(initial_position=initial_position, controller=controller, **kwargs)

        self.eye_l = Eye(self.head, [-8, 8], angle_offset=math.pi / 4, rotation_range=math.pi, name='left_eye')
        self.add_body_part(self.eye_l)

        self.eye_r = Eye(self.head, [8, 8], angle_offset=-math.pi / 4, rotation_range=math.pi, name='rigth_eye')
        self.add_body_part(self.eye_r)

        # New Key maps
        self.eye_l.angular_velocity_actuator.assign_key(K_h, KeyTypes.PRESS_HOLD, 1)
        self.eye_l.angular_velocity_actuator.assign_key(K_j, KeyTypes.PRESS_HOLD, -1)

        self.eye_r.angular_velocity_actuator.assign_key(K_k, KeyTypes.PRESS_HOLD, 1)
        self.eye_r.angular_velocity_actuator.assign_key(K_l, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class TurretAgent(Agent):

    """
    Agent with a Head.
    Base is fixed.

    Attributes:
        head: Head of the agent
    """

    def __init__(self, initial_position=None, controller=None, **kwargs):

        base_agent = FixedPlatform(radius=15)
        super().__init__(initial_position=initial_position, base_platform=base_agent, **kwargs)

        self.head = Head(base_agent, [0, 0], angle_offset=0, rotation_range=math.pi, radius=10, name='head')
        self.add_body_part(self.head)

        # New Key maps
        self.head.angular_velocity_actuator.assign_key(K_LEFT, KeyTypes.PRESS_HOLD, 1)
        self.head.angular_velocity_actuator.assign_key(K_RIGHT, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class ArmAgent(HeadAgent):
    """
        Agent with two Arms.

        Attributes:
            head: Head of the agent
            arm_l: left arm
            arm_l_2: second segment of left arm
            arm_r: right arm
            arm_r_2: second segment of right arm
        """
    def __init__(self, initial_position=None, controller=None, **kwargs):

        super().__init__(initial_position=initial_position, controller=controller, **kwargs)

        self.arm_r = Arm(self.base_platform, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.arm_l = Arm(self.base_platform, [-15, 0], angle_offset=math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_l)

        self.arm_l_2 = Arm(self.arm_l, self.arm_l.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_l_2)

        self.arm_r.angular_velocity_actuator.assign_key(K_v, KeyTypes.PRESS_HOLD, 1)
        self.arm_r.angular_velocity_actuator.assign_key(K_b, KeyTypes.PRESS_HOLD, -1)

        self.arm_r_2.angular_velocity_actuator.assign_key(K_x, KeyTypes.PRESS_HOLD, 1)
        self.arm_r_2.angular_velocity_actuator.assign_key(K_c, KeyTypes.PRESS_HOLD, -1)

        self.arm_l.angular_velocity_actuator.assign_key(K_f, KeyTypes.PRESS_HOLD, 1)
        self.arm_l.angular_velocity_actuator.assign_key(K_g, KeyTypes.PRESS_HOLD, -1)

        self.arm_l_2.angular_velocity_actuator.assign_key(K_s, KeyTypes.PRESS_HOLD, 1)
        self.arm_l_2.angular_velocity_actuator.assign_key(K_d, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class ArmHandAgent(BaseInteractiveAgent):
    """
        Agent with an Arm and a Hand attached to this arm.

        Attributes:
            arm_r: right arm
            arm_r_2: second segment of right arm
            hand_r: hand attached to arm_r_2
        """
    def __init__(self, initial_position=None,controller = None, **kwargs):

        base_agent = HolonomicPlatform(radius=15)

        super(ArmHandAgent, self).__init__(initial_position=initial_position, controller=controller, **kwargs)

        self.base_platform.shape_filter = pymunk.ShapeFilter(group=1)

        self.arm_r = Arm(self.base_platform, [15, 0], angle_offset=-math.pi / 2, rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r, self.arm_r.extremity_anchor_point, rotation_range=9 * math.pi / 5)
        self.add_body_part(self.arm_r_2)

        self.hand_r = Hand(self.arm_r_2, self.arm_r_2.extremity_anchor_point, radius=8, rotation_range=math.pi)
        self.add_body_part(self.hand_r)

        self.arm_r.angular_velocity_actuator.assign_key(K_v, KeyTypes.PRESS_HOLD, 1)
        self.arm_r.angular_velocity_actuator.assign_key(K_b, KeyTypes.PRESS_HOLD, -1)

        self.arm_r_2.angular_velocity_actuator.assign_key(K_x, KeyTypes.PRESS_HOLD, 1)
        self.arm_r_2.angular_velocity_actuator.assign_key(K_c, KeyTypes.PRESS_HOLD, -1)

        self.arm_r_2.angular_velocity_actuator.assign_key(K_g, KeyTypes.PRESS_HOLD, 1)
        self.arm_r_2.angular_velocity_actuator.assign_key(K_f, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller
