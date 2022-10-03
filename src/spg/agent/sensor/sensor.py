"""
Module defining the Base Classes for Sensors.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import numpy as np

from ...entity import EmbodiedEntity
from ..device import PocketDevice

SensorValue = Union[np.ndarray, List[np.ndarray]]


SENSOR_COLOR = (23, 24, 113)


class Sensor(PocketDevice):
    """Base class Sensor, used as an Interface for all sensors.

    Attributes:
        anchor: Part or Element to which the sensor is attached.
            Sensor is attached to the center of the anchor.
        sensor_values: current values of the sensor.
        name: Name of the sensor.

    Note:
        The anchor is always invisible to the sensor.

    """

    def __init__(
        self,
        normalize: Optional[bool] = False,
        **kwargs,
    ):
        """
        Sensors are attached to an anchor.
        They can detect any visible Part of an Agent or Elements of the Playground.
        If the entity is in invisible elements, it is not detected.

        Args:
            anchor: Body Part or Scene Element on which the sensor will be attached.
            normalize: boolean. If True, sensor values are scaled between 0 and 1.
            noise_params: Dictionary of noise parameters.
                Noise is applied to the raw sensor, before normalization.
            name: name of the sensor. If not provided, a name will be set by default.

        Noise Parameters:
            type: 'gaussian', 'salt_pepper'
            mean: mean of gaussian noise (default 0)
            scale: scale (or std) of gaussian noise (default 1)
            salt_pepper_probability: probability for a pixel to be turned off or max

        """

        super().__init__(color=SENSOR_COLOR, **kwargs)

        self._values = None

        self._normalize = normalize

        self._noise = False

    def update(self):

        if self._disabled:
            self._values = self._default_value

        else:
            self._compute_raw_sensor()

            if self._noise:
                self._apply_noise()

            if self._normalize:
                self._apply_normalization()

    @abstractmethod
    def _compute_raw_sensor(self):
        ...

    @abstractmethod
    def _apply_normalization(self):
        ...

    def _apply_noise(self):
        """
        Implement this method on custom sensors to add noise to the values.
        """

    @property
    @abstractmethod
    def _default_value(self) -> np.ndarray:
        ...

    @property
    @abstractmethod
    def shape(self) -> tuple:
        """Returns the shape of the numpy array, if applicable."""

    @abstractmethod
    def draw(self):
        ...


##################
# Range Sensors
##################


class ExternalSensor(Sensor, ABC):
    def __init__(
        self,
        fov: float,
        resolution: int,
        max_range: float,  # pylint: disable=redefined-builtin
        invisible_elements: Optional[
            Union[List[EmbodiedEntity], EmbodiedEntity]
        ] = None,
        invisible_when_grasped: bool = False,
        **kwargs,
    ):
        """

        Args:
            fov: Field of view of the sensor (in degrees).
            resolution: Resolution of the sensor (depends on the sensor).
            range: maximum range of the sensor (in units of distance).
            invisible_elements: Optional list of elements invisible to the sensor.
            **kwargs:

        """

        super().__init__(**kwargs)

        self._invisible_elements: List[EmbodiedEntity]

        # Invisible elements
        if not invisible_elements:
            self._invisible_elements = []
        elif isinstance(invisible_elements, EmbodiedEntity):
            self._invisible_elements = [invisible_elements]
        else:
            self._invisible_elements = invisible_elements

        self._range = max_range
        self._fov = fov * math.pi / 180
        self._resolution = resolution

        if self._resolution < 0:
            raise ValueError("resolution must be more than 1")
        if self._fov < 0:
            raise ValueError("field of view must be more than 1")
        if self._range < 0:
            raise ValueError("range must be more than 1")

        self._temporary_invisible: List[EmbodiedEntity] = []
        self._invisible_grasped = invisible_when_grasped
        self._require_invisible_update = False

    @property
    def max_range(self):
        return self._range

    @property
    def fov(self):
        return self._fov

    @property
    def resolution(self):
        return self._resolution

    @property
    def invisible_ids(self):
        return [ent.uid for ent in self._temporary_invisible + self._invisible_elements]

    @property
    def invisible_grasped(self):
        return self._invisible_grasped

    @property
    def require_invisible_update(self):
        return self._require_invisible_update

    def add_to_temporary_invisible(self, elem):
        self._temporary_invisible.append(elem)
        self._require_invisible_update = True

    def remove_from_temporary_invisible(self, elem):
        self._temporary_invisible.remove(elem)
        self._require_invisible_update = True

    def pre_step(self):
        super().pre_step()
        self._require_invisible_update = False
