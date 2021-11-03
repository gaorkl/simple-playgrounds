from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.element.element import SceneElement

import numpy as np
import pymunk
from PIL import ImageFont, ImageDraw

from simple_playgrounds.agent.parts import Part, AnchoredPart, Platform
from simple_playgrounds.common.definitions import LINEAR_FORCE, ANGULAR_VELOCITY, KeyTypes
from simple_playgrounds.device.device import Device


class ActuatorDevice(Device, ABC):
    """
    Actuator classes defines how one body part acts.
    It is used to control parts of an agent:
        - physical actions (movements)
        - interactive actions (eat, grasp, ...)
    """
    def __init__(
        self,
        part,
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """

        Args:
            part (Part): part that the Actuator is controlling.
            noise_params: Dictionary of noise parameters.
                Noise is applied to the actuator, before action.

        Noise Parameters:
            type: 'gaussian'
            mean: mean of gaussian noise (default 0)
            scale: scale / std of gaussian noise (default 1)
        """

        Device.__init__(self, anchor=part)

        self.part = part
        self.command: float = 0
        self.value: float = 0
        self.has_key_mapping: bool = False
        self.key_map: Dict = {}

        # Motor noise
        self._noise = noise
        if self._noise:

            if not noise_params:
                raise ValueError('Noise params not set')
            self._parse_noise_params(noise_params)

        part.add_actuator(self)

    def assign_key(self, key: int, key_behavior: KeyTypes, value: float):
        """
        Assign keyboard key to a value.

        Args:
            key: PyGame keyboard key.
            key_behavior: KeyTypes.PRESS_HOLD or KeyTypes.PRESS_ONCE
            value: value of the actuator when key is pressed.

        """
        self.has_key_mapping = True
        self.key_map[key] = [key_behavior, value]

    def pre_step(self):
        super().pre_step()
        self.value = self.default_value

    def apply_action(
        self,
        value,
    ):

        self.command = value

        if self._disabled:
            value = self.default_value

        else:

            if not self._check_action_value(value):
                raise ValueError(
                    "Value for command {} not compatible".format(value))

            if self._noise:
                value = self._apply_noise(value)

        self._apply_action(value)

    @abstractmethod
    def _apply_action(self, value):
        ...

    @abstractmethod
    def _check_action_value(self, value) -> bool:
        ...

    @abstractmethod
    def _apply_noise(self, value):
        ...

    @abstractmethod
    def _parse_noise_params(
        self,
        noise_params: Dict[str, float],
    ):
        ...

    @abstractmethod
    def draw(self, drawer_action_image: ImageDraw, img_width: int,
             position_height: int, height_action: int, fnt: ImageFont):
        ...

    @property
    @abstractmethod
    def default_value(self) -> float:
        pass

    @property
    @abstractmethod
    def min(self) -> float:
        pass

    @property
    @abstractmethod
    def max(self) -> float:
        pass


# DISCRETE ACTUATORS


class DiscreteActuator(ActuatorDevice, ABC):
    """
    Discrete Actuators are initialized by providing a list of valid actuator values.
    Then, an action is applied by providing the index of the desired actuator value.
    """
    def __init__(
        self,
        part: Part,
        actuator_values: Tuple[float, ...],
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
    ):
        """

        Args:
            part (Part): part that the Actuator is controlling.
            actuator_values: list or tuple of discrete values.
        """
        super().__init__(part, noise=noise, noise_params=noise_params)

        if not isinstance(actuator_values, (list, tuple)):
            raise ValueError('Set of values must be list or tuple')

        self.actuator_values = actuator_values

    def _check_action_value(
        self,
        action_index: int,
    ) -> bool:
        if action_index in range(self.range):
            return True
        return False

    def reset(self):
        self.value = self.default_value

    @property
    def default_value(self) -> float:
        return 0

    @property
    def min(self) -> float:
        return min(self.actuator_values)

    @property
    def max(self) -> float:
        return max(self.actuator_values)

    @property
    def argmin(self) -> int:
        """
        Index of the action of minimum value.
        """
        return self.actuator_values.index(self.min)

    @property
    def argmax(self) -> int:
        """
        Index of the action of maximum value.
        """
        return self.actuator_values.index(self.max)

    @property
    def range(self) -> int:
        """
        Returns the number of actions for this actuator.
        """
        return len(self.actuator_values)


class InteractionActuator(DiscreteActuator, ABC):
    """
    Base class for Interaction Actuators.
    Interaction Actuators are binary actuators.
    """
    def __init__(
        self,
        part: Part,
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
    ):

        super().__init__(part,
                         actuator_values=(0, 1),
                         noise=noise,
                         noise_params=noise_params)

    def draw(self, drawer_action_image, img_width, position_height,
             height_action, fnt):

        if self.value == 1:
            start = (0, position_height)
            end = (img_width, position_height + height_action)
            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        w_text, h_text = fnt.getsize(text=type(self).__name__)
        pos_text = (img_width / 2.0 - w_text / 2,
                    position_height + height_action / 2 - h_text / 2)
        drawer_action_image.text(pos_text,
                                 type(self).__name__,
                                 font=fnt,
                                 fill=(0, 0, 0))

    def _parse_noise_params(
        self,
        noise_params: Dict[str, float],
    ):

        if self._noise == 'random_flip':
            self._proba_flip: float = noise_params.get('probability', 0)

        else:
            raise ValueError('Noise type not implemented')

    def _apply_noise(
        self,
        action_index: int,
    ) -> int:

        if self._noise == 'random_flip':
            flip = random.choices(
                [True, False],
                weights=[self._proba_flip, 1 - self._proba_flip])

            if flip:
                action_index = 1 - action_index

            return action_index

        else:
            raise ValueError('Noise type not implemented')


class Activate(InteractionActuator):
    def __init__(self, part):
        super().__init__(part)
        self.is_activating = 0

    def _apply_action(self, value):
        self.is_activating = self.actuator_values[value]


class Grasp(InteractionActuator):
    def __init__(self, part):
        super().__init__(part)

        self.is_grasping = False

        self.grasped_element: Optional[SceneElement] = None
        self._grasp_joints = []

    def _apply_action(self, value):

        self.is_grasping = self.actuator_values[value]

        if self.grasped_element and not self.is_grasping:
            self.release_grasp()

    def grasp(self, grasped_element: SceneElement):

        j_1 = pymunk.PinJoint(self.part.pm_body,
                              grasped_element.pm_body, (0, 0),
                              (0, 20))
        j_2 = pymunk.PinJoint(self.part.pm_body,
                              grasped_element.pm_body, (0, 0),
                              (0, -20))

        j_3 = pymunk.PinJoint(self.part.pm_body,
                              grasped_element.pm_body, (0, 20),
                              (0, 0))
        j_4 = pymunk.PinJoint(self.part.pm_body,
                              grasped_element.pm_body, (0, -20),
                              (0, 0))

        self._grasp_joints = [j_1, j_2, j_3, j_4]
        self.part.pm_body.space.add(*self._grasp_joints)

        self.grasped_element = grasped_element
        grasped_element.held_by = self

    def release_grasp(self):

        for joint in self._grasp_joints:
            self.part.pm_body.space.remove(joint)
        self._grasp_joints = []
        self.grasped_element.released_by(self)
        self.grasped_element = None

# CONTINUOUS ACTUATORS


class ContinuousActuator(ActuatorDevice, ABC):
    def __init__(
        self,
        part,
        centered: bool = True,
        action_range: float = 1,
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
    ):
        """

        Args:
            part: part that the actuator is affecting
            centered: if True, actions are in [-1, 1]. If False, actions are in [0, 1].
            action_range: multiplication factor for the action.
        """
        super().__init__(part, noise=noise, noise_params=noise_params)

        self._centered = centered
        self._action_range = action_range

    def _check_action_value(
        self,
        value: float,
    ) -> bool:

        if self.centered:
            if -1 <= value <= 1:
                return True
            return False
        else:
            if 0 <= value <= 1:
                return True
            return False

    def draw(self, drawer_action_image, img_width, position_height,
             height_action, fnt):

        if self.centered and self.value != 0:

            if self.value < 0:
                left = int(img_width / 2. + self.value * img_width / 2.)
                right = int(img_width / 2.)
            else:
                right = int(img_width / 2. + self.value * img_width / 2.)
                left = int(img_width / 2.)

            start = (left, position_height)
            end = (right, position_height + height_action)

            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        elif not self.centered and self.value != 0:

            left = int(img_width / 2.)
            right = int(img_width / 2. + self.value * img_width / 2.)

            start = (left, position_height)
            end = (right, position_height + height_action)

            drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

        w_text, h_text = fnt.getsize(text=type(self).__name__)
        drawer_action_image.text(
            (img_width / 2.0 - w_text / 2,
             position_height + height_action / 2 - h_text / 2),
            type(self).__name__,
            font=fnt,
            fill=(0, 0, 0))

    @property
    def default_value(self) -> float:
        return 0

    @property
    def centered(self) -> bool:
        return self._centered

    @property
    def min(self) -> float:
        if self.centered:
            return -1
        return 0

    @property
    def max(self) -> float:
        return 1

    def _apply_noise(
        self,
        value: float,
    ) -> float:

        if self._noise == 'gaussian':

            value += random.gauss(self._mean, self._scale)

            value = value if value > self.min else self.min
            value = value if value < self.max else self.max

            return value

        else:
            raise ValueError('Noise type not implemented')

    def _parse_noise_params(
        self,
        noise_params: Dict[str, float],
    ):

        if self._noise == 'gaussian':

            self._mean = noise_params.get('mean', 0)
            self._scale = noise_params.get('scale', 0.01)

        else:
            raise ValueError('Noise type not implemented')


class ForceActuator(ContinuousActuator, ABC):
    def __init__(
        self,
        part: Platform,
        centered: bool = True,
        action_range: float = 1,
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
    ):

        super().__init__(part, centered, action_range, noise, noise_params)

        assert isinstance(self.part, Platform)


class LongitudinalForce(ForceActuator):
    def _apply_action(self, value: float):

        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(value, 0) * LINEAR_FORCE * self._action_range, (0, 0))


class LateralForce(ForceActuator):

    def _apply_action(self, value: float):
        self.part.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(0, value) * self._action_range * LINEAR_FORCE, (0, 0))


class AngularVelocity(ForceActuator):

    def _apply_action(self, value: float):
        self.part.pm_body.angular_velocity = value * ANGULAR_VELOCITY * self._action_range


class MotorActuator(ContinuousActuator, ABC):
    def __init__(
        self,
        part: AnchoredPart,
        centered: bool = True,
        action_range: float = 1,
        noise: Optional[str] = None,
        noise_params: Optional[Dict[str, float]] = None,
    ):

        assert isinstance(part, AnchoredPart)
        self.part: AnchoredPart

        super().__init__(part, centered, action_range, noise, noise_params)


class AngularRelativeVelocity(MotorActuator):
    def _apply_action(self, value: float):

        self.part: AnchoredPart

        theta_part = self.part.angle
        theta_anchor = self.part.anchor.angle

        angle_centered = (theta_part - (theta_anchor + self.part.angle_offset))
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (angle_centered - 2 * np.pi
                          if angle_centered > np.pi else angle_centered)

        # Do not set the motor if the limb is close to limit
        if (angle_centered <
                -self.part.rotation_range / 2 + np.pi / 20) and value < 0:
            self.part.motor.rate = 0

        elif (angle_centered >
              self.part.rotation_range / 2 - np.pi / 20) and value > 0:
            self.part.motor.rate = 0

        else:
            self.part.motor.rate = -value * ANGULAR_VELOCITY * self._action_range
