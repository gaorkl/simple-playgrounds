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
from simple_playgrounds.agents.parts.parts import Head, Hand, Eye, Arm, FixedPlatform, MobilePlatform
from simple_playgrounds.utils.definitions import KeyTypes
from simple_playgrounds.agents.parts.actuators import AngularVelocity, LongitudinalForce, LateralForce, Grasp, Eat, Activate, AngularRelativeVelocity


# pylint: disable=undefined-variable


class BaseAgent(Agent):
    """
    Class for Base Agents: single platform without extra body parts.
    Base agent absorb through their base
    """

    def __init__(self,
                 controller,
                 rotate=True,
                 forward=True,
                 backward=True,
                 lateral=False,
                 interactive=False,
                 name=None,
                 **kwargs):
        """
        Base Agent, with a single platform as a body.

        Args:
            controller: controller of the agent.
            platform: Platform (FixedPlatform or MobilePlatform)
            interactive: if interactive, can eat/grasp/activate/absorb
            **kwargs: additional kwargs for the base

        Keyword Args:
            radius: radius of the platform. Default 15.

        """

        if not (forward or backward or lateral or rotate):
            base = FixedPlatform(name='base', can_absorb=True, **kwargs)

        else:
            base = MobilePlatform(name='base', can_absorb=True, **kwargs)

        super().__init__(base_platform=base, name=name)

        if forward:

            if backward:
                actuator = LongitudinalForce(base)
                actuator.assign_key(K_UP, KeyTypes.PRESS_HOLD, 1)
                actuator.assign_key(K_DOWN, KeyTypes.PRESS_HOLD, -1)
            else:
                actuator = LongitudinalForce(base, centered=False)
                actuator.assign_key(K_UP, KeyTypes.PRESS_HOLD, 1)

            self.add_actuator(actuator)

        if lateral:
            actuator = LateralForce(base)
            actuator.assign_key(K_v, KeyTypes.PRESS_HOLD, -1)
            actuator.assign_key(K_b, KeyTypes.PRESS_HOLD, 1)
            self.add_actuator(actuator)

        if rotate:
            actuator = AngularVelocity(base)
            actuator.assign_key(K_RIGHT, KeyTypes.PRESS_HOLD, 1)
            actuator.assign_key(K_LEFT, KeyTypes.PRESS_HOLD, -1)
            self.add_actuator(actuator)

        if interactive:
            grasp_actuator = Grasp(base)
            grasp_actuator.assign_key(K_g, KeyTypes.PRESS_HOLD, 1)
            self.add_actuator(grasp_actuator)

            activate_actuator = Activate(base)
            activate_actuator.assign_key(K_a, KeyTypes.PRESS_ONCE, 1)
            self.add_actuator(activate_actuator)

            eat_actuator = Eat(base)
            eat_actuator.assign_key(K_e, KeyTypes.PRESS_ONCE, 1)
            self.add_actuator(eat_actuator)

        # Assign controller once all body parts are declared
        self.controller = controller


class HeadAgent(BaseAgent):
    """
    Platform with a Head.

    Attributes:
        head: Head of the agent
    """

    def __init__(self, controller, **kwargs):

        super().__init__(controller, **kwargs)

        self.head = Head(self.base_platform,
                         position_anchor=[0, 0],
                         radius=self.base_platform.radius - 4,
                         angle_offset=0,
                         rotation_range=math.pi,
                         name='head')
        self.add_body_part(self.head)

        head_actuator = AngularRelativeVelocity(self.head)
        head_actuator.assign_key(K_n, KeyTypes.PRESS_HOLD, -1)
        head_actuator.assign_key(K_m, KeyTypes.PRESS_HOLD, 1)

        self.add_actuator(head_actuator)

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

    def __init__(self, controller, **kwargs):

        super().__init__(controller=controller, **kwargs)

        self.eye_l = Eye(self.head,
                         position_anchor=[self.head.radius/2, -self.head.radius/2],
                         angle_offset=-math.pi / 5,
                         rotation_range=2*math.pi/3,
                         name='left_eye')
        self.add_body_part(self.eye_l)

        eye_l_actuator = AngularVelocity(self.eye_l)
        eye_l_actuator.assign_key(K_d, KeyTypes.PRESS_HOLD, 1)
        eye_l_actuator.assign_key(K_f, KeyTypes.PRESS_HOLD, 1)
        self.add_actuator(eye_l_actuator)

        self.eye_r = Eye(self.head, position_anchor=[self.head.radius/2, self.head.radius/2],
                         angle_offset=math.pi / 5,
                         rotation_range=2*math.pi/3,
                         name='right_eye')
        self.add_body_part(self.eye_r)

        eye_r_actuator = AngularVelocity(self.eye_r)
        eye_r_actuator.assign_key(K_h, KeyTypes.PRESS_HOLD, 1)
        eye_r_actuator.assign_key(K_j, KeyTypes.PRESS_HOLD, -1)
        self.add_actuator(eye_r_actuator)

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

        arm_r_actuator = AngularVelocity(self.arm_r)
        arm_r_actuator.assign_key(K_r, KeyTypes.PRESS_HOLD, 1)
        arm_r_actuator.assign_key(K_t, KeyTypes.PRESS_HOLD, -1)
        self.add_actuator(arm_r_actuator)

        self.arm_r_2 = Arm(self.arm_r,
                           position_anchor=self.arm_r.extremity_anchor_point,
                           angle_offset=-math.pi / 4,
                           rotation_range=math.pi)
        self.add_body_part(self.arm_r_2)

        arm_r_2_actuator = AngularVelocity(self.eye_l)
        arm_r_2_actuator.assign_key(K_y, KeyTypes.PRESS_HOLD, 1)
        arm_r_2_actuator.assign_key(K_u, KeyTypes.PRESS_HOLD, -1)
        self.add_actuator(arm_r_2_actuator)

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

        arm_l_actuator = AngularVelocity(self.arm_l)
        arm_l_actuator.assign_key(K_i, KeyTypes.PRESS_HOLD, 1)
        arm_l_actuator.assign_key(K_o, KeyTypes.PRESS_HOLD, -1)
        self.add_actuator(arm_l_actuator)

        self.arm_l_2 = Arm(self.arm_l,
                           position_anchor=self.arm_l.extremity_anchor_point,
                           angle_offset=math.pi/4,
                           rotation_range=math.pi)
        self.add_body_part(self.arm_l_2)

        arm_l_2_actuator = AngularVelocity(self.arm_l_2)
        arm_l_2_actuator.assign_key(K_k, KeyTypes.PRESS_HOLD, 1)
        arm_l_2_actuator.assign_key(K_l, KeyTypes.PRESS_HOLD, -1)
        self.add_actuator(arm_l_2_actuator)

        self.hand_l = Hand(self.arm_l_2,
                           position_anchor=self.arm_l_2.extremity_anchor_point,
                           radius=8,
                           rotation_range=0,
                           can_grasp=interactive,
                           can_activate=interactive)
        self.add_body_part(self.hand_l)

        # Assign controller once all body parts are declared
        self.controller = controller
