from ...entities.entity import Entity
from ...utils.config import *

import pymunk
import pygame
import math
import yaml
import os
from abc import ABC, abstractmethod


class Part(Entity, ABC):
    """
    Base class for Body Parts.
    Part inherits from Entity. It is a visible, movable Entity.

    """

    entity_type = 'part'
    part_type = None

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: Optional Keyword Arguments

        Keyword Args:
            can_absorb (:obj: 'bool'): If True, body part can absorb absorbable entities on contact. Default: False
            can_eat (:obj: 'bool'): If True, body part can eat edible entities. Default: False
            can_activate (:obj: 'bool'): If True, body part can activate activable entities. Default: False
            can_grasp (:obj: 'bool'): If True, body part can grasp graspable entities. Default: False

        Note:
            All properties related to the physical properties of the Part can be set as keyword argument.
            Refer to the Entity class for the list of available keyword arguments.

        """

        Entity.__init__(self, initial_position=[0, 0, 0], visible=True, movable=True, **kwargs)
        self.pm_visible_shape.collision_type = CollisionTypes.AGENT

        self.can_absorb = kwargs.get('can_absorb', False)
        self.can_eat = kwargs.get('can_eat', False)
        self.can_activate = kwargs.get('can_activate', False)
        self.can_grasp = kwargs.get('can_grasp', False)
        self.grasped = []

        self.is_eating = False
        self.is_activating = False
        self.is_grasping = False
        self.is_holding = False

    @staticmethod
    def _parse_configuration(part_type):
        """
        Method to parse yaml configuration file.

        Args:
            part_type (str): Can be 'platform', 'eye', 'hand', 'arm', 'hand'

        Returns:
            Dictionary containing the default configuration of the body part.

        """

        fname = 'parts_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[part_type]

    @abstractmethod
    def get_available_actions(self):
        """
        Method that create a :obj: 'list' of :obj: 'Action'.
        An :obj:'Action' is a namedtuple (see Action in the definitions)

        Returns:
            List of available actions :obj: 'list' of :obj: 'Action'.

        """
        actions = []

        if self.can_grasp:
            actions.append(Action(self.name, ActionTypes.GRASP, ActionTypes.DISCRETE, 0, 1))

        if self.can_activate:
            actions.append(Action(self.name, ActionTypes.ACTIVATE, ActionTypes.DISCRETE, 0, 1))

        if self.can_eat:
            actions.append(Action(self.name, ActionTypes.EAT, ActionTypes.DISCRETE, 0, 1))

        return actions

    @abstractmethod
    def apply_actions(self, actions):
        """
        Apply the actions to the physical body part

        Args:
            actions (:obj: 'dict'): dictionary of actions. keys are ActionTypes, values are floats.

        """

        if self.can_activate:
            self.is_activating = actions.get(ActionTypes.ACTIVATE, False)

        if self.can_eat:
            self.is_eating = actions.get(ActionTypes.EAT, False)

        if self.can_grasp:
            self.is_grasping = actions.get(ActionTypes.GRASP, False)

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

        pass

    @abstractmethod
    def reset(self):

        super().reset()

        if self.can_activate:
            self.is_activating = False
        if self.can_eat:
            self.is_eating = False
        if self.can_grasp:
            self.is_grasping = False
            self.grasped = []
            self.is_holding = False


class Platform(Part, ABC):

    """
    Base class for Platforms.
    Inherits from Part.
    An agent requires a Platform to build its body.

    """

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs: optional additional parameters

        Keyword Args:
            physical_shape (str): circle, square, pentagon, hexagon. Default: circle
            texture (:obj: 'dict': dictionary of texture parameters
            radius: radius of the platform. Default: 20
            mass: mass of the platform. Default: 10
            max_linear_velocity: Maximum longitudinal and lateral velocity (pixels per timestep). Default: 1.0
            max_angular_velocity: Maximum angular velocity (radian per timestep). Default: 0.25
        """

        default_config = self._parse_configuration('platform')
        body_part_params = {**default_config, **kwargs}

        super().__init__(**body_part_params)

        self.max_linear_velocity = body_part_params['max_linear_velocity']
        self.max_angular_velocity = body_part_params['max_angular_velocity']

    def reset(self):
        super().reset()

    def create_visible_mask(self):

        mask = super().create_visible_mask()

        y = self.radius * (1 + math.cos(self.pm_body.angle))
        x = self.radius * (1 + math.sin(self.pm_body.angle))
        pygame.draw.line(mask, pygame.color.THECOLORS["blue"], (self.radius, self.radius), (x, y), 2)

        return mask


class ForwardPlatform(Platform):

    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def get_available_actions(self):
        actions = super().get_available_actions()

        actions.append(Action(self.name, ActionTypes.LONGITUDINAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1))
        actions.append(Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1))

        return actions

    def apply_actions(self, actions):

        super().apply_actions(actions)

        longitudinal_velocity = actions.get(ActionTypes.LONGITUDINAL_VELOCITY, 0)
        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        # TODO: Check this, SIMULATION STEPS should disappear.
        vx = longitudinal_velocity * SIMULATION_STEPS
        vy = 0
        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(vx, vy) * self.max_linear_velocity * (1.0 - SPACE_DAMPING) * 100, (0, 0))
        self.pm_body.angular_velocity = angular_velocity * self.max_angular_velocity


class HolonomicPlatform(ForwardPlatform):

    """
    Platform that can translate in all directions, and rotate.
    Refer to the base class Platform.
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def get_available_actions(self):

        actions = super().get_available_actions()

        actions.append(Action(self.name, ActionTypes.LATERAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1))

        return actions

    def apply_actions(self, actions):

        super().apply_actions(actions)
        lateral_velocity = actions.get(ActionTypes.LATERAL_VELOCITY, 0)

        # TODO: Check this, SIMULATION STEPS should disappear.
        vx = 0
        vy = lateral_velocity * SIMULATION_STEPS
        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(vx, vy) * self.max_linear_velocity * (1.0 - SPACE_DAMPING) * 100, (0, 0))


class Actuator(Part, ABC):

    """
    Base class for Actuators.
    Contains methods to calculate coordinates of anchor points, create joints and motors between actuator and anchor.

    Attributes:
        anchor:
        joint:
        limit:
        motor:

    """

    def __init__(self, anchor, coord_anchor=(0, 0), coord_part=(0, 0), angle_offset=0, **kwargs):

        """
        An Actuator is attached to an other Part (anchor).
        They are joined at a single point.
        An Actuator can never collide with its Anchor.

        Args:
            anchor: Part on which the new Actuator will be attached
            coord_anchor: coordinates of the joint on the anchor. Default: (0,0)
            coord_part: coordinates of the joint on the actuator. Default: (0,0)
            angle_offset: angle offset od the actuator compared to the anchor (in rads). Default: 0
            **kwargs: additional Keyword Parameters
        """

        self.anchor = anchor

        super().__init__(**kwargs)

        self.max_angular_velocity = kwargs['max_angular_velocity']
        self.rotation_range = kwargs['rotation_range']

        self.angle_offset = angle_offset

        self.relative_position_of_anchor_on_anchor = coord_anchor
        self.relative_position_of_anchor_on_part = coord_part

        self.set_relative_position()

        x0, y0 = self.relative_position_of_anchor_on_anchor
        x1, y1 = self.relative_position_of_anchor_on_part

        self.joint = pymunk.PivotJoint(anchor.pm_body, self.pm_body,  (y0, -x0), ( y1, -x1))
        self.joint.collide_bodies = False
        self.limit = pymunk.RotaryLimitJoint(anchor.pm_body, self.pm_body,
                                        self.angle_offset - self.rotation_range/2 ,
                                        self.angle_offset + self.rotation_range/2)

        self.motor = pymunk.SimpleMotor(anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [self.joint, self.motor, self.limit]

    def set_relative_position(self):

        # Get position of the anchor point on anchor
        x_anchor_center, y_anchor_center = self.anchor.pm_body.position
        x_anchor_center, y_anchor_center = -y_anchor_center, x_anchor_center
        theta_anchor = (self.anchor.pm_body.angle + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_anchor, y_anchor_relative_of_anchor = self.relative_position_of_anchor_on_anchor

        x_anchor_coordinates_anchor = x_anchor_center + x_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2 ) -\
                                      y_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2 )
        y_anchor_coordinates_anchor = y_anchor_center + x_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2 ) + \
                                      y_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2 )

        # Get position of the anchor point on part
        theta_part = (self.anchor.pm_body.angle + self.angle_offset + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_part, y_anchor_relative_of_part = self.relative_position_of_anchor_on_part

        x_anchor_coordinates_part =  x_anchor_relative_of_part * math.cos(theta_part - math.pi / 2) - \
                                      y_anchor_relative_of_part * math.sin(theta_part - math.pi / 2)
        y_anchor_coordinates_part =  x_anchor_relative_of_part * math.sin(theta_part - math.pi / 2) + \
                                      y_anchor_relative_of_part * math.cos(theta_part - math.pi / 2)

        # Move part to align on anchor
        y = -(x_anchor_coordinates_anchor - x_anchor_coordinates_part)
        x = y_anchor_coordinates_anchor - y_anchor_coordinates_part
        self.pm_body.position = ( x, y )

        self.pm_body.angle = self.anchor.pm_body.angle + self.angle_offset

    def get_available_actions(self):

        actions = []

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)
        actions.append(action)


        return actions


    def apply_actions(self, actions):

        super().apply_actions(actions)

        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        self.motor.rate = angular_velocity * self.max_angular_velocity

        ### Case when theta close to limit -> speed to zero
        theta_part = self.position[2]
        theta_anchor = self.anchor.position[2]

        angle_centered = (theta_part - (theta_anchor+self.angle_offset))%(2*math.pi)
        angle_centered = angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered

        # Do not set the motor if the limb is close to limit
        if angle_centered < - self.rotation_range/2 + math.pi/20 and angular_velocity > 0 :
            self.motor.rate = 0

        elif angle_centered > self.rotation_range/2 - math.pi/20 and angular_velocity < 0 :
            self.motor.rate = 0

    def reset(self):
        super().reset()


class Head(Actuator):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self._parse_configuration('head')
        default_config['rotation_range'] *= math.pi / 180

        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        position_part = [0,0]

        super(Head, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.pm_visible_shape.sensor = True

    def create_visible_mask(self):

        mask = super().create_visible_mask()

        y = self.radius * (1 + math.cos(self.pm_body.angle))
        x = self.radius * (1 + math.sin(self.pm_body.angle))
        pygame.draw.line(mask, pygame.color.THECOLORS["green"], (self.radius, self.radius), (x, y), 2)

        return mask



class Eye(Actuator):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self._parse_configuration('eye')
        body_part_params = {**default_config, **kwargs}

        # Eye attached in its center
        position_part = [0,0]

        super(Eye, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.pm_visible_shape.sensor = True

    def create_visible_mask(self,):

        mask = super().create_visible_mask()

        angle = self.pm_body.angle

        y = self.radius * (1 + math.cos(angle))
        x = self.radius * (1 + math.sin(angle))
        pygame.draw.line(mask, pygame.color.THECOLORS["brown"], (self.radius, self.radius), (x, y), 2)

        return mask


class Hand(Actuator):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self._parse_configuration( 'hand')
        body_part_params = {**default_config, **kwargs}

        # hand attached in its center
        position_part = [0,0]

        super(Hand, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)


class Arm(Actuator):

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = self._parse_configuration( 'arm')
        body_part_params = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchr point defined at other extremity
        width, length = body_part_params['width_length']
        position_part = [0, -length/2.0 + width/2.0]

        self.extremity_anchor_point = [0, length/2.0 - width/2.0]

        super(Arm, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.motor.max_force = 500
