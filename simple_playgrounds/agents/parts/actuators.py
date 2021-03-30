from abc import ABC, abstractmethod
import numpy as np
import pymunk

from simple_playgrounds.utils.definitions import ActionSpaces, LINEAR_FORCE, ANGULAR_VELOCITY


class Actuator(ABC):
    """
    Actuator classes defines how one body acts.
    It is used to define physical movements as well as interactions (eat, grasp, ...)
    of parts of an agent.
    """

    action_space = None

    def __init__(self, part):
        """

        Args:
            part (Part): part that the Actuator is controlling.
        """

        self.part = part

        self.has_key_mapping = False
        self.key_map = {}

    def assign_key(self, key, key_behavior, value):
        """
        Assign keyboard key to a value.

        Args:
            key: PyGame keyboard key.
            key_behavior: KeyTypes.PRESS_HOLD or KeyTypes.PRESS_ONCE
            value: value of the actuator when key is pressed.

        """
        self.has_key_mapping = True
        self.key_map[key] = [key_behavior, value]

    @abstractmethod
    def _check_value(self, value):
        pass

    @abstractmethod
    def apply_action(self, value):
        pass

    @abstractmethod
    def min(self):
        pass

    @abstractmethod
    def max(self):
        pass


class InteractionActuator(Actuator, ABC):

    action_space = ActionSpaces.BINARY

    def _check_value(self, value):
        assert value in [0, 1]

    @property
    def min(self):
        return 0

    @property
    def max(self):
        return 1


class Activate(InteractionActuator):

    def apply_action(self, value):

        self._check_value(value)
        self.part.is_activating = value


class Eat(InteractionActuator):

    def apply_action(self, value):

        self._check_value(value)
        self.part.is_eating = value


class Grasp(InteractionActuator):

    def apply_action(self, value):
        self._check_value(value)
        self.part.is_grasping = value

        if self.part.is_holding and not self.part.is_grasping:
            self.part.is_holding = False


class PhysicalActuator(Actuator, ABC):

    action_space = ActionSpaces.CONTINUOUS

    def __init__(self, part, centered=True, action_range=1):
        """

        Args:
            part: part that the actuator is affecting
            centered: if True, values are in [-1, 1]. If False, values are in [0, 1].
            action_range: multiplication factor for the values.
        """
        super().__init__(part)

        self.centered = centered
        self._action_range = action_range

    def _check_value(self, value):

        if self.centered:
            assert -1 <= value <= 1
        else:
            assert 0 <= value <= 1

    @property
    def min(self):
        if self.centered:
            return -1
        return 0

    @property
    def max(self):
        return 1


class LongitudinalForce(PhysicalActuator):

    def apply_action(self, value):
        self._check_value(value)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(value, 0) * LINEAR_FORCE * self._action_range, (0, 0))


class LateralForce(PhysicalActuator):

    def apply_action(self, value):
        self._check_value(value)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(0, -value) * self._action_range * LINEAR_FORCE, (0, 0))


class AngularVelocity(PhysicalActuator):

    def apply_action(self, value):
        self._check_value(value)
        self.part.pm_body.angular_velocity = value * ANGULAR_VELOCITY * self._action_range


class AngularRelativeVelocity(PhysicalActuator):

    def apply_action(self, value):
        self._check_value(value)

        theta_part = self.part.angle
        theta_anchor = self.part.anchor.angle

        angle_centered = (theta_part - (theta_anchor + self.part.angle_offset))
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (angle_centered - 2 * np.pi
                          if angle_centered > np.pi else angle_centered)

        # Do not set the motor if the limb is close to limit
        if (angle_centered <
            -self.part.rotation_range / 2 + np.pi / 20) and value > 0:
            self.part.motor.rate = 0

        elif (angle_centered >
              self.part.rotation_range / 2 - np.pi / 20) and value < 0:
            self.part.motor.rate = 0

        else:
            self.part.motor.rate = value * ANGULAR_VELOCITY * self._action_range

