from abc import ABC, abstractmethod
import numpy as np
import pymunk

from simple_playgrounds.utils.definitions import ActionSpaces, LINEAR_FORCE, ANGULAR_VELOCITY


class Actuator(ABC):
    """
    Actuator classes defines how one body part acts.
    It is used to control parts of an agent:
        - physical actions (movements)
        - interactive actions (eat, grasp, ...)
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

    @abstractmethod
    def default_value(self):
        pass

    @abstractmethod
    def min(self):
        pass

    @abstractmethod
    def max(self):
        pass


# DISCRETE ACTUATORS

class DiscreteActuator(Actuator, ABC):
    """
    Discrete Actuators are initialized by providing a list of valid actuator values.
    Then, an action is applied by providing the index of the desired actuator value.
    """

    action_space = ActionSpaces.DISCRETE

    def __init__(self, part, actuator_values):
        """

        Args:
            part (Part): part that the Actuator is controlling.
            actuator_values: list or tuple of discrete values.
        """
        super().__init__(part)

        if not isinstance(actuator_values, (list, tuple)):
            raise ValueError('Set of values must be list or tuple')

        self.actuator_values = actuator_values

    def _pre_step(self, action_index):
        assert action_index in range(self.range)
        self.current_value = action_index

    @abstractmethod
    def apply_action(self, action_index):
        """
        Apply action receives the index of the action applied to the part.

        Args:
            action_index: index of the action, in {0, 1, .. self.range-1}.
        """
        pass

    @property
    def default_value(self):
        return 0

    @property
    def min(self):
        return min(self.actuator_values)

    @property
    def max(self):
        return max(self.actuator_values)

    @property
    def argmin(self):
        """
        Index of the action of minimum value.
        """
        return self.actuator_values.index(self.min)

    @property
    def argmax(self):
        """
        Index of the action of maximum value.
        """
        return self.actuator_values.index(self.max)

    @property
    def range(self):
        """
        Returns the number of actions for this actuator.
        """
        return len(self.actuator_values)


class InteractionActuator(DiscreteActuator, ABC):
    """
    Base class for Interaction Actuators.
    Interaction Actuators are binary actuators.
    """

    def __init__(self, part):
        super().__init__(part, actuator_values=(0, 1))

    def draw(self, drawer_action_image, position_height, height_action, fnt):

        img_width, _ = drawer_action_image.im.size

        if self.current_value == 1:
            start = (0, position_height)
            end = (img_width, position_height + height_action)
            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        w_text, h_text = fnt.getsize(text=type(self).__name__)
        pos_text = (img_width/2.0 - w_text/2,
                    position_height+height_action/2 - h_text/2)
        drawer_action_image.text(pos_text, type(self).__name__, font=fnt, fill=(0, 0, 0))


class Activate(InteractionActuator):

    def apply_action(self, action_index):

        self._pre_step(action_index)
        self.part.is_activating = self.actuator_values[action_index]


class Eat(InteractionActuator):

    def apply_action(self, action_index):

        self._pre_step(action_index)
        self.part.is_eating = self.actuator_values[action_index]


class Grasp(InteractionActuator):

    def apply_action(self, action_index):
        self._pre_step(action_index)
        self.part.is_grasping = self.actuator_values[action_index]

        if self.part.is_holding and not self.part.is_grasping:
            self.part.is_holding = False


# CONTINUOUS ACTUATORS


class ContinuousActuator(Actuator, ABC):

    action_space = ActionSpaces.CONTINUOUS

    def __init__(self, part, centered=True, action_range=1):
        """

        Args:
            part: part that the actuator is affecting
            centered: if True, actions are in [-1, 1]. If False, actions are in [0, 1].
            action_range: multiplication factor for the action.
        """
        super().__init__(part)

        self._centered = centered
        self._action_range = action_range

    def _pre_step(self, action):

        if self.centered:
            assert -1 <= action <= 1
        else:
            assert 0 <= action <= 1

        self.current_value = action

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

    @abstractmethod
    def apply_action(self, action):
        """
        Applies a continuous action to an actuator.
        The continuous action is a product of the value (in [0, 1] or [-1,1]) and the action range.
            
        Args:
            action: 

        Returns:

        """
        pass

    @property
    def default_value(self):
        return 0

    @property
    def centered(self):
        return self._centered

    @property
    def min(self):
        if self.centered:
            return -1
        return 0

    @property
    def max(self):
        return 1


class LongitudinalForce(ContinuousActuator):

    def apply_action(self, action):
        self._pre_step(action)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(action, 0) * LINEAR_FORCE * self._action_range, (0, 0))


class LateralForce(ContinuousActuator):

    def apply_action(self, action):
        self._pre_step(action)

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(0, action) * self._action_range * LINEAR_FORCE, (0, 0))


class AngularVelocity(ContinuousActuator):

    def apply_action(self, action):
        self._pre_step(action)
        self.part.pm_body.angular_velocity = action * ANGULAR_VELOCITY * self._action_range


class AngularRelativeVelocity(ContinuousActuator):

    def apply_action(self, action):
        self._pre_step(action)

        theta_part = self.part.angle
        theta_anchor = self.part.anchor.angle

        angle_centered = (theta_part - (theta_anchor + self.part.angle_offset))
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (angle_centered - 2 * np.pi
                          if angle_centered > np.pi else angle_centered)

        # Do not set the motor if the limb is close to limit
        if (angle_centered <
            -self.part.rotation_range / 2 + np.pi / 20) and action > 0:
            self.part.motor.rate = 0

        elif (angle_centered >
              self.part.rotation_range / 2 - np.pi / 20) and action < 0:
            self.part.motor.rate = 0

        else:
            self.part.motor.rate = action * ANGULAR_VELOCITY * self._action_range

