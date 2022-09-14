from abc import ABC

import numpy as np

from .sensor import ExternalSensor


class RaySensor(ExternalSensor, ABC):
    """
    Base class for Ray Based sensors.
    Ray sensors use Arcade shaders
    """

    def __init__(
        self,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self._hit_positions = np.zeros((self._resolution, 2))
        self._hit_values = np.zeros(self.shape)
