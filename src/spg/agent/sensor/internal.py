from abc import ABC

from .sensor import Sensor

##################
# Internal Sensors
##################


class InternalSensor(Sensor, ABC):

    """
    Base Class for Internal Sensors.
    """
