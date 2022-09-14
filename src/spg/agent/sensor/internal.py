from abc import ABC

import numpy as np

from .sensor import Sensor

##################
# Internal Sensors
##################


class InternalSensor(Sensor, ABC):

    """
    Base Class for Internal Sensors.
    """

    def _default_value(self):
        return np.zeros(self.shape)
