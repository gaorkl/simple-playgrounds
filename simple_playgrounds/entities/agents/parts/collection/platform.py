"""
Body Parts of an Agent.
"""

import math
from abc import ABC

import pymunk
import pygame

from simple_playgrounds.entities.agents.parts.part import Part
from simple_playgrounds.utils import ActionTypes, Action

# pylint: disable=line-too-long


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
            physical_shape (str): circle, square, pentagon, hexagon. Default: circle.
            texture (:obj: 'dict': dictionary of texture parameters.
            radius: radius of the platform. Default: 20.
            mass: mass of the platform. Default: 15.
            max_linear_force: Maximum longitudinal and lateral force. Default: 0.3.
            max_angular_velocity: Maximum angular velocity (radian per timestep). Default: 0.25.
        """

        default_config = self._parse_configuration('platform')
        body_part_params = {**default_config, **kwargs}

        Part.__init__(self, **body_part_params)

        self.max_linear_force = body_part_params['max_linear_force']
        self.max_angular_velocity = body_part_params['max_angular_velocity']
        self.max_longitudinal_velocity = body_part_params['max_longitudinal_velocity']

    # def _create_mask(self, is_interactive=False):
    #
    #     mask = Part._create_mask(self)
    #
    #     # pos_y = self.radius + (self.radius-2) * (math.cos(self.pm_body.angle))
    #     # pos_x = self.radius + (self.radius-2) * (math.sin(self.pm_body.angle))
    #     # pygame.draw.line(mask, pygame.color.THECOLORS["blue"],
    #     #                  (self.radius, self.radius), (pos_x, pos_y), 2)
    #
    #     return mask


class FixedPlatform(Platform):
    """
        Platform that is fixed.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """

    movable = False

    def get_available_actions(self):

        return []

    def apply_actions(self, actions):
        pass

class ForwardPlatform(Platform):

    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def get_available_actions(self):
        actions = super().get_available_actions()

        actions.append(Action(self.name, ActionTypes.LONGITUDINAL_FORCE, ActionTypes.CONTINUOUS_CENTERED, -1, 1))
        actions.append(Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS_CENTERED, -1, 1))

        return actions

    def apply_actions(self, actions):

        super().apply_actions(actions)

        lateral_force = actions.get(ActionTypes.LONGITUDINAL_FORCE, 0)
        self.pm_body.apply_force_at_local_point(pymunk.Vec2d(lateral_force, 0) * self.max_linear_force * 100, (0, 0))

        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)
        self.pm_body.angular_velocity = angular_velocity * self.max_angular_velocity


class HolonomicPlatform(ForwardPlatform):

    """
    Platform that can translate in all directions, and rotate.
    Refer to the base class Platform.
    """

    def get_available_actions(self):

        actions = super().get_available_actions()

        actions.append(Action(self.name, ActionTypes.LATERAL_FORCE, ActionTypes.CONTINUOUS_CENTERED, -1, 1))

        return actions

    def apply_actions(self, actions):

        super().apply_actions(actions)
        lateral_force = actions.get(ActionTypes.LATERAL_FORCE, 0)

        self.pm_body.apply_force_at_local_point(pymunk.Vec2d(0, lateral_force) * self.max_linear_force * 100, (0, 0))
