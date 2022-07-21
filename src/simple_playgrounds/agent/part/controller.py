from __future__ import annotations
from collections import defaultdict
import random
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, TYPE_CHECKING, Union, List

if TYPE_CHECKING:
    from simple_playgrounds.element.element import SceneElement
    from simple_playgrounds.agent.part.part import Part

import numpy as np
import pymunk
from PIL import ImageFont, ImageDraw

Command = Union[float, int, bool]


class Controller(ABC):
    """
    Command classes define how parts can be controlled.
    It is used to control parts of an agent:
        - physical actions (movements)
        - interactive actions (eat, grasp, ...)
    """

    def __init__(self, part: Part, name: Optional[str] = None, hard_check=True, **_):
        self._part: Part = part

        if not name:
            name = part.agent.get_name(self)

        self._name = name

        self._noise: bool = False
        self._disabled: bool = False

        self._command = self.default
        self._hard_check = hard_check

    @property
    def rng(self):
        return self._part.rng

    @property
    @abstractmethod
    def default(self) -> Command:
        ...

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        check_passed = self._check(command)

        if not check_passed and self._hard_check:
            raise ValueError(command)

        # Maybe replace by closest later?
        if not check_passed:
            command = self.default

        self._command = command

    @property
    def name(self):
        return self._name

    def pre_step(self):
        self._command = self.default

    def reset(self):
        self.pre_step()

    @abstractmethod
    def _check(self, command) -> bool:
        ...

    @abstractmethod
    def _apply_noise(self, command, no_noise=False, **_) -> Command:
        ...

    @property
    def command_value(self) -> Command:
        if self._noise:
            return self._apply_noise(self._command)
        return self._command

    @abstractmethod
    def draw(
        self,
        drawer_action_image: ImageDraw,
        img_width: int,
        position_height: int,
        height_action: int,
        fnt: ImageFont,
    ):
        ...


####################
# DISCRETE COMMANDS
####################


class DiscreteController(Controller):
    """
    Discrete Commands.
    Command values can take a number within a list of integers.
    0 is always the default command, even if not given at initialization.
    """

    def __init__(
        self,
        command_values: List[int],
        **kwargs,
    ):
        super().__init__(**kwargs)

        if not isinstance(command_values, (list, tuple)):
            raise ValueError("Set of values must be list or tuple")

        self._valid_command_values = command_values

        self._change_proba: float = self._get_noise_params(**kwargs)

    def _get_noise_params(
        self, error_probability: Optional[float] = None, **_
    ) -> float:

        if not error_probability:
            self._noise = False
            return 0

        self._noise = True
        return error_probability

    def _check(self, command, hard_check=True, **_) -> Command:
        return command in self._valid_command_values

    def _apply_noise(
        self,
        command: int,
        no_noise: Optional[bool] = False,
        **_,
    ) -> int:

        if no_noise:
            return command

        proba = self.rng.random()

        if proba < self._change_proba:
            command = self.command_value

        return command

    @property
    def default(self) -> int:
        return 0

    @property
    def valid_commands(self):
        return self._valid_command_values

    def draw(
        self,
        drawer_action_image: ImageDraw,
        img_width: int,
        position_height: int,
        height_action: int,
        fnt: ImageFont,
    ):
        pass

    # def draw(self, drawer_action_image, img_width, position_height,
    #          height_action, fnt):

    #     if self.command == 1:
    #         start = (0, position_height)
    #         end = (img_width, position_height + height_action)
    #         drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

    #     w_text, h_text = fnt.getsize(text=type(self).__name__)
    #     pos_text = (img_width / 2.0 - w_text / 2,
    #                 position_height + height_action / 2 - h_text / 2)
    #     drawer_action_image.text(pos_text,
    #                              type(self).__name__,
    #                              font=fnt,
    #                              fill=(0, 0, 0))


class BoolController(DiscreteController):
    def __init__(self, **kwargs):
        super().__init__(command_values=[0, 1], **kwargs)

    @property
    def default(self) -> int:
        return 0


class RangeController(DiscreteController):
    def __init__(self, n: int, **kwargs):
        super().__init__(command_values=list(range(n)), **kwargs)


###################
# ContinuousCommand
###################


class ContinuousController(Controller, ABC):
    def __init__(self, min_value: float, max_value: float, **kwargs):

        super().__init__(**kwargs)

        if min_value > max_value:
            raise ValueError

        self._min = min_value
        self._max = max_value

    def _check(self, command) -> bool:

        return self._min <= command <= self._max

    @property
    def default(self) -> float:
        return 0

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    def _apply_noise(self, command, no_noise, **_) -> Command:

        if self._noise == "gaussian":

            value = random.gauss(self._mean, self._scale)

            value = value if value > self.min else self.min
            value = value if value < self.max else self.max

            return value

        else:
            raise ValueError("Noise type not implemented")

    def _parse_noise_params(
        self,
        noise_params: Dict[str, float],
        **_,
    ):

        if self._noise == "gaussian":

            self._mean = noise_params.get("mean", 0)
            self._scale = noise_params.get("scale", 0.01)

        else:
            raise ValueError("Noise type not implemented")

    def draw(
        self,
        drawer_action_image: ImageDraw,
        img_width: int,
        position_height: int,
        height_action: int,
        fnt: ImageFont,
    ):
        pass


class CenteredContinuousController(ContinuousController):
    def __init__(self, **kwargs):
        super().__init__(min_value=-1, max_value=1, **kwargs)


class NormalContinuousController(ContinuousController):
    def __init__(self, **kwargs):
        super().__init__(min_value=0, max_value=1, **kwargs)

    # def draw(self, drawer_action_image, img_width, position_height,
    #          height_action, fnt):

    #     if self.centered and self.command != 0:

    #         if self.value < 0:
    #             left = int(img_width / 2. + self.command * img_width / 2.)
    #             right = int(img_width / 2.)
    #         else:
    #             right = int(img_width / 2. + self.command * img_width / 2.)
    #             left = int(img_width / 2.)

    #         start = (left, position_height)
    #         end = (right, position_height + height_action)

    #         drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

    #     elif not self.centered and self.command != 0:

    #         left = int(img_width / 2.)
    #         right = int(img_width / 2. + self.command * img_width / 2.)

    #         start = (left, position_height)
    #         end = (right, position_height + height_action)

    #         drawer_action_image.rectangle([start, end], fill=(20, 200, 20))

    #     w_text, h_text = fnt.getsize(text=type(self).__name__)
    #     drawer_action_image.text(
    #         (img_width / 2.0 - w_text / 2,
    #          position_height + height_action / 2 - h_text / 2),
    #         type(self).__name__,
    #         font=fnt,
    #         fill=(0, 0, 0))


# class ForceActuator(ContinuousActuator, ABC):
#     def __init__(
#         self,
#         part: Platform,
#         centered: bool = True,
#         action_range: float = 1,
#         noise: Optional[str] = None,
#         noise_params: Optional[Dict[str, float]] = None,
#     ):

#         super().__init__(part, centered, action_range, noise, noise_params)

#         assert isinstance(self.part, Platform)


# class LongitudinalForce(ForceActuator):
#     def _apply_action(self, value: float):

#         self.part.pm_body.apply_force_at_local_point(
#             pymunk.Vec2d(value, 0) * LINEAR_FORCE * self._action_range, (0, 0))


# class LateralForce(ForceActuator):

#     def _apply_action(self, value: float):
#         self.part.pm_body.apply_force_at_local_point(
#             pymunk.Vec2d(0, value) * self._action_range * LINEAR_FORCE, (0, 0))


# class AngularVelocity(ForceActuator):

#     def _apply_action(self, value: float):
#         self.part.pm_body.angular_velocity = value * ANGULAR_VELOCITY * self._action_range


# class MotorActuator(ContinuousActuator, ABC):
#     def __init__(
#         self,
#         part: AnchoredPart,
#         centered: bool = True,
#         action_range: float = 1,
#         noise: Optional[str] = None,
#         noise_params: Optional[Dict[str, float]] = None,
#     ):

#         assert isinstance(part, AnchoredPart)
#         self.part: AnchoredPart

#         super().__init__(part, centered, action_range, noise, noise_params)


# class AngularRelativeVelocity(MotorActuator):
#     def _apply_action(self, value: float):

#         self.part: AnchoredPart

#         theta_part = self.part.angle
#         theta_anchor = self.part.anchor.angle

#         angle_centered = (theta_part - (theta_anchor + self.part.angle_offset))
#         angle_centered = angle_centered % (2 * np.pi)
#         angle_centered = (angle_centered - 2 * np.pi
#                           if angle_centered > np.pi else angle_centered)

#         # Do not set the motor if the limb is close to limit
#         if (angle_centered <
#                 -self.part.rotation_range / 2 + np.pi / 20) and value < 0:
#             self.part.motor.rate = 0

#         elif (angle_centered >
#               self.part.rotation_range / 2 - np.pi / 20) and value > 0:
#             self.part.motor.rate = 0

#         else:
#             self.part.motor.rate = -value * ANGULAR_VELOCITY * self._action_range
