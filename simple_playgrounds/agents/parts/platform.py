""" Module implementing Platform.

A Platform is a Part which serves as the base to attach other Links.
Platform is controlled by longitudinal or lateral force, and angular velocity.
"""

from abc import ABC

import pymunk

from simple_playgrounds.agents.parts.part import Part, Actuator
from simple_playgrounds.utils.definitions import ActionTypes, AgentPartTypes, ActionSpaces,\
    LINEAR_FORCE, ANGULAR_VELOCITY
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods


class Platform(Part, ABC):
    """
    Base class for Platforms.
    Inherits from Part.
    An agent requires a Platform to build its body.

    """

    entity_type = AgentPartTypes.PLATFORM

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs: optional additional parameters

        Keyword Args:
            physical_shape (str): circle, square, pentagon, hexagon. Default: circle.
            texture (:obj: 'dict': dictionary of texture parameters.
            radius: radius of the platform. Default: 20.
            mass: mass of the platform. Default: 15.
        """

        default_config = parse_configuration('agent_parts', self.entity_type)
        body_part_params = {**default_config, **kwargs}

        Part.__init__(self, **body_part_params)


class FixedPlatform(Platform):
    """
        Platform that is fixed.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """

    movable = False


class ForwardPlatform(Platform):
    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.longitudinal_force_actuator = Actuator(self.name, ActionTypes.LONGITUDINAL_FORCE,
                                                    ActionSpaces.CONTINUOUS_POSITIVE)
        self.actuators.append(self.longitudinal_force_actuator)

        self.angular_velocity_actuator = Actuator(self.name, ActionTypes.ANGULAR_VELOCITY,
                                                  ActionSpaces.CONTINUOUS_CENTERED)
        self.actuators.append(self.angular_velocity_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        self._check_value_actuator(actuator, value)

        if actuator is self.longitudinal_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(value, 0) * LINEAR_FORCE, (0, 0))

        if actuator is self.angular_velocity_actuator:
            self.pm_body.angular_velocity = value * ANGULAR_VELOCITY

        return value


class ForwardPlatformDiscrete(ForwardPlatform):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.longitudinal_force_actuator = Actuator(self.name, ActionTypes.LONGITUDINAL_FORCE,
                                                    ActionSpaces.DISCRETE_POSITIVE)
        self.angular_velocity_actuator = Actuator(self.name, ActionTypes.ANGULAR_VELOCITY,
                                                  ActionSpaces.DISCRETE_CENTERED)


class ForwardBackwardPlatform(ForwardPlatform):
    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.actuators.remove(self.longitudinal_force_actuator)

        self.longitudinal_force_actuator = Actuator(self.name, ActionTypes.LONGITUDINAL_FORCE,
                                                    ActionSpaces.CONTINUOUS_CENTERED)
        self.actuators.append(self.longitudinal_force_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        self._check_value_actuator(actuator, value)

        if actuator is self.longitudinal_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(value, 0) * LINEAR_FORCE, (0, 0))

        if actuator is self.angular_velocity_actuator:
            self.pm_body.angular_velocity = value * ANGULAR_VELOCITY

        return value


class HolonomicPlatform(ForwardBackwardPlatform):
    """
    Platform that can translate in all directions, and rotate.
    Refer to the base class Platform.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.lateral_force_actuator = Actuator(self.name, ActionTypes.LATERAL_FORCE, ActionSpaces.CONTINUOUS_CENTERED)
        self.actuators.append(self.lateral_force_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        self._check_value_actuator(actuator, value)

        if actuator is self.lateral_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(0, -value) * LINEAR_FORCE, (0, 0))

        return value
