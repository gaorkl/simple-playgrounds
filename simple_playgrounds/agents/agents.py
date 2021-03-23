""" Module implementing standard agents.

These standard agents have body parts and associated Keyboard mappings.
They can be used as is, and sensors can be added to any body part.

Typical Usage:

    my_agent = HeadAgent(controller=Keyboard(), platform=ForwardBackwardPlatform, interactive=True)

    rgb = RgbCamera(my_agent.head, invisible_elements=my_agent.parts, resolution=64, max_range=600)
    my_agent.add_sensor(rgb)

    my_playground.add_agent(my_agent)

"""
import math

# pylint: disable=unused-wildcard-import
from pygame.locals import *  # pylint: disable=wildcard-import

from simple_playgrounds.agent import Agent
from simple_playgrounds.agents.parts import Head, Hand, Eye, Arm, FixedPlatform
from simple_playgrounds.utils.definitions import KeyTypes, ActionSpaces

# pylint: disable=undefined-variable


class BaseAgent(Agent):
    """
    Class for Base Agents: single platform without extra body parts.
    """

    def __init__(self, controller=None, platform=None, interactive=False,
                 **kwargs):
        """
        Base Agent, with a single platform as a body.

        Args:
            initial_position: initial position of the agent (Position, or PositionAreaSampler)
            controller: controller of the agent.
            platform: Platform object
                (HolonomicPlatform, FixedPlatform, ForwardPlatform, ForwardBackwardPlatform)
            interactive: if interactive, can eat/grasp/activate/absorb
            **kwargs: additional kwargs

        Keyword Args:
            radius: radius of the platform. Default 15.

        """

        radius_platform = kwargs.get('radius', 15)

        base_agent = platform(name='base', radius=radius_platform,
                              can_eat=interactive,
                              can_grasp=interactive,
                              can_activate=interactive,
                              can_absorb=interactive)

        super().__init__(base_platform=base_agent, **kwargs)

        if hasattr(self.base_platform, 'longitudinal_force_actuator'):

            self.base_platform.longitudinal_force_actuator.assign_key(K_UP, KeyTypes.PRESS_HOLD, 1)

            if self.base_platform.longitudinal_force_actuator.action_space \
                    is ActionSpaces.CONTINUOUS_CENTERED:
                self.base_platform.longitudinal_force_actuator.assign_key(K_DOWN,
                                                                          KeyTypes.PRESS_HOLD,
                                                                          -1)

        if hasattr(self.base_platform, 'lateral_force_actuator'):

            self.base_platform.lateral_force_actuator.assign_key(K_b,
                                                                 KeyTypes.PRESS_HOLD, 1)
            self.base_platform.lateral_force_actuator.assign_key(K_v,
                                                                 KeyTypes.PRESS_HOLD, -1)

        if hasattr(self.base_platform, 'angular_velocity_actuator'):

            self.base_platform.angular_velocity_actuator.assign_key(K_RIGHT,
                                                                    KeyTypes.PRESS_HOLD, 1)
            self.base_platform.angular_velocity_actuator.assign_key(K_LEFT,
                                                                    KeyTypes.PRESS_HOLD, -1)

        if interactive:
            self.base_platform.eat_actuator.assign_key(K_e, KeyTypes.PRESS_ONCE, 1)
            self.base_platform.activate_actuator.assign_key(K_a, KeyTypes.PRESS_ONCE, 1)
            self.base_platform.grasp_actuator.assign_key(K_g, KeyTypes.PRESS_HOLD, 1)

        # Assign controller once all body parts are declared
        self.controller = controller


class HeadAgent(BaseAgent):
    """
    Platform with a Head.

    Attributes:
        head: Head of the agent
    """

    def __init__(self,
                 controller=None,
                 platform=None,
                 interactive=False,
                 **kwargs):

        super().__init__(controller=controller,
                         platform=platform, interactive=interactive, **kwargs)

        self.head = Head(self.base_platform,
                         position_anchor=[0, 0],
                         radius=self.base_platform.radius - 4,
                         angle_offset=0,
                         rotation_range=math.pi,
                         name='head')

        self.add_body_part(self.head)

        # Key maps
        self.head.angular_velocity_actuator.assign_key(K_n, KeyTypes.PRESS_HOLD, 1)
        self.head.angular_velocity_actuator.assign_key(K_m, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class HeadEyeAgent(HeadAgent):
    """
    Platform with a Head, and Two eyes attached to the head.

    Attributes:
        head: Head of the agent
        eye_l: Left Eye
        eye_r: Right Eye
    """

    def __init__(self,
                 controller=None,
                 platform=None,
                 interactive=False,
                 **kwargs):

        super().__init__(controller=controller,
                         platform=platform, interactive=interactive, **kwargs)

        self.eye_l = Eye(self.head,
                         position_anchor=[self.head.radius/2, -self.head.radius/2],
                         angle_offset=-math.pi / 5,
                         rotation_range=2*math.pi/3,
                         name='left_eye')
        self.add_body_part(self.eye_l)

        self.eye_r = Eye(self.head, position_anchor=[self.head.radius/2, self.head.radius/2],
                         angle_offset=math.pi / 5,
                         rotation_range=2*math.pi/3,
                         name='right_eye')
        self.add_body_part(self.eye_r)

        # New Key maps
        self.eye_l.angular_velocity_actuator.assign_key(K_d, KeyTypes.PRESS_HOLD, 1)
        self.eye_l.angular_velocity_actuator.assign_key(K_f, KeyTypes.PRESS_HOLD, -1)

        self.eye_r.angular_velocity_actuator.assign_key(K_h, KeyTypes.PRESS_HOLD, 1)
        self.eye_r.angular_velocity_actuator.assign_key(K_j, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller


class TurretAgent(HeadAgent):

    """
    Agent with a Head.
    Base is fixed.

    Attributes:
        head: Head of the agent
    """

    def __init__(self, controller=None, interactive=False, platform=None, **kwargs):

        super().__init__(platform=FixedPlatform,
                         controller=controller, interactive=interactive, **kwargs)

        # Assign controller once all body parts are declared
        self.controller = controller


class FullAgent(HeadEyeAgent):
    """
        Agent with two Arms. Experimental, not fully operational.

        Attributes:
            head: Head of the agent
            arm_l: left arm
            arm_l_2: second segment of left arm
            hand_l: left hand.
            arm_r: right arm
            arm_r_2: second segment of right arm
            hand_r: right hand

        Notes:
            if interactive, the agent grasp and activate with hands, and absorb and eats with body.

        """
    def __init__(self,
                 controller=None,
                 platform=None,
                 interactive=False,
                 **kwargs):

        super().__init__(platform=platform, controller=controller, interactive=interactive,
                         **kwargs)

        self.base_platform.can_grasp = False
        self.base_platform.can_activate = False

        self.arm_r = Arm(self.base_platform,
                         position_anchor=[0, self.base_platform.radius],
                         angle_offset=math.pi/4,
                         rotation_range=math.pi)
        self.add_body_part(self.arm_r)

        self.arm_r_2 = Arm(self.arm_r,
                           position_anchor=self.arm_r.extremity_anchor_point,
                           angle_offset=-math.pi / 4,
                           rotation_range=math.pi)
        self.add_body_part(self.arm_r_2)

        self.hand_r = Hand(self.arm_r_2,
                           position_anchor=self.arm_r_2.extremity_anchor_point,
                           radius=8,
                           rotation_range=0,
                           can_grasp=interactive,
                           can_activate=interactive)
        self.add_body_part(self.hand_r)

        self.arm_l = Arm(self.base_platform,
                         position_anchor=[0, -self.base_platform.radius],
                         angle_offset=-math.pi / 4,
                         rotation_range=math.pi)
        self.add_body_part(self.arm_l)

        self.arm_l_2 = Arm(self.arm_l,
                           position_anchor=self.arm_l.extremity_anchor_point,
                           angle_offset=math.pi/4,
                           rotation_range=math.pi)
        self.add_body_part(self.arm_l_2)

        self.hand_l = Hand(self.arm_l_2,
                           position_anchor=self.arm_l_2.extremity_anchor_point,
                           radius=8,
                           rotation_range=0,
                           can_grasp=interactive,
                           can_activate=interactive)
        self.add_body_part(self.hand_l)

        self.arm_r.angular_velocity_actuator.assign_key(K_r, KeyTypes.PRESS_HOLD, 1)
        self.arm_r.angular_velocity_actuator.assign_key(K_t, KeyTypes.PRESS_HOLD, -1)

        self.arm_r_2.angular_velocity_actuator.assign_key(K_y, KeyTypes.PRESS_HOLD, 1)
        self.arm_r_2.angular_velocity_actuator.assign_key(K_u, KeyTypes.PRESS_HOLD, -1)

        self.arm_l.angular_velocity_actuator.assign_key(K_i, KeyTypes.PRESS_HOLD, 1)
        self.arm_l.angular_velocity_actuator.assign_key(K_o, KeyTypes.PRESS_HOLD, -1)

        self.arm_l_2.angular_velocity_actuator.assign_key(K_k, KeyTypes.PRESS_HOLD, 1)
        self.arm_l_2.angular_velocity_actuator.assign_key(K_l, KeyTypes.PRESS_HOLD, -1)

        # Assign controller once all body parts are declared
        self.controller = controller
