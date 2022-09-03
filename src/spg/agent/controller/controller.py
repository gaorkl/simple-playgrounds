from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, TYPE_CHECKING, Union, List

from ..device import PocketDevice
import numpy as np


if TYPE_CHECKING:
    from ..part import PhysicalPart

Command = Union[float, int, bool]

CONTROLLER_COLOR = (123, 234, 213)


class Controller(PocketDevice):
    """
    Command classes define how parts can be controlled.
    It is used to control parts of an agent:
        - physical actions (movements)
        - interactive actions (eat, grasp, ...)
    """

    def __init__(self, hard_check=True, **_):

        super().__init__(color=CONTROLLER_COLOR)

        self._noise: bool = False
        self._disabled: bool = False

        self._command = self.default
        self._hard_check = hard_check

    @property
    def _rng(self):
        if self._playground:
            return self._playground._rng
        else:
            return np.random.default_rng()

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

    def pre_step(self):
        self._command = self.default
        self._disabled = False

    def disable(self):
        self._disabled = True

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

        proba = self._rng.random()

        if proba < self._change_proba:
            command = self.command_value

        return command

    @property
    def default(self) -> int:
        return 0

    @property
    def valid_commands(self):
        return self._valid_command_values


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


class CenteredContinuousController(ContinuousController):
    def __init__(self, **kwargs):
        super().__init__(min_value=-1, max_value=1, **kwargs)


class NormalContinuousController(ContinuousController):
    def __init__(self, **kwargs):
        super().__init__(min_value=0, max_value=1, **kwargs)
