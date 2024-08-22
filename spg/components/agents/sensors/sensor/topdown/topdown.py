from abc import ABC

from spg.core.entity.interaction.sensor import SensorMixin


class TopDownSensor(SensorMixin, ABC):

    """
    Base class for Image Based sensors.
    Image based sensors are computed using the top-down rendering of the playground.

    """

    pass
