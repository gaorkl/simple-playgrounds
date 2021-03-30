from abc import ABC, abstractmethod
import numpy as np
import pymunk
from PIL import ImageFont
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
        self.current_value = 0
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
    def _pre_step(self, value):
        pass

    @abstractmethod
    def apply_action(self, value):
        pass

    @abstractmethod
    def draw(self, drawer_action_image, position_height, height_action, fnt):
        pass


# DISCRETE ACTUATORS

class DiscreteActuator(Actuator, ABC):

    action_space = ActionSpaces.DISCRETE

    def __init__(self, part, value_set):

        super().__init__(part)

        if not isinstance(value_set, (list, tuple)):
            raise ValueError('Set of values must be list or tuple')

        self.value_set = value_set

    def _pre_step(self, value):
        assert value in self.value_set
        self.current_value = value


class InteractionActuator(DiscreteActuator, ABC):

    def __init__(self, part):
        super().__init__(part, value_set=(0, 1))

    def draw(self, drawer_action_image, position_height, height_action, fnt):

        img_width, _ = drawer_action_image.im.size

        if self.current_value == 1:
            start = (0, position_height)
            end = (img_width, position_height + height_action)
            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        w_text, h_text = fnt.getsize(text=type(self).__name__)
        drawer_action_image.text((img_width / 2.0 - w_text / 2, position_height + height_action / 2 - h_text / 2),
                          type(self).__name__,
                          font=fnt, fill=(0, 0, 0))


class Activate(InteractionActuator):

    def apply_action(self, value):

        self._pre_step(value)
        self.part.is_activating = value


class Eat(InteractionActuator):

    def apply_action(self, value):

        self._pre_step(value)
        self.part.is_eating = value


class Grasp(InteractionActuator):

    def apply_action(self, value):
        self._pre_step(value)
        self.part.is_grasping = value

        if self.part.is_holding and not self.part.is_grasping:
            self.part.is_holding = False


# CONTINUOUS ACTUATORS


class ContinuousActuator(Actuator, ABC):

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

    def _pre_step(self, value):

        if self.centered:
            assert -1 <= value <= 1
        else:
            assert 0 <= value <= 1

        self.current_value = value

    def draw(self, drawer_action_image, position_height, height_action, fnt):

        img_width, _ = drawer_action_image.im.size

        if self.centered and self.current_value != 0:

            if self.current_value < 0:
                left = int(img_width / 2. + self.current_value * img_width / 2.)
                right = int(img_width / 2.)
            else:
                right = int(img_width / 2. + self.current_value * img_width / 2.)
                left = int(img_width / 2.)

            start = (left, position_height)
            end = (right, position_height + height_action)

            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        elif not self.centered and self.current_value != 0:

            left = int(img_width / 2.)
            right = int(img_width / 2. + self.current_value * img_width / 2.)

            start = (left, position_height)
            end = (right, position_height + height_action)

            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        w_text, h_text = fnt.getsize(text=type(self).__name__)
        drawer_action_image.text((img_width / 2.0 - w_text / 2, position_height + height_action / 2 - h_text / 2),
                         type(self).__name__,
                         font=fnt, fill=(0, 0, 0))


class LongitudinalForce(ContinuousActuator):

    def apply_action(self, value):
        self._pre_step(value)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(value, 0) * LINEAR_FORCE * self._action_range, (0, 0))


class LateralForce(ContinuousActuator):

    def apply_action(self, value):
        self._pre_step(value)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(0, value) * self._action_range * LINEAR_FORCE, (0, 0))


class AngularVelocity(ContinuousActuator):

    def apply_action(self, value):
        self._pre_step(value)
        self.part.pm_body.angular_velocity = value * ANGULAR_VELOCITY * self._action_range


class AngularRelativeVelocity(ContinuousActuator):

    def apply_action(self, value):
        self._pre_step(value)

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

