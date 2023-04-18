import math
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


class Position(InternalSensor):

    """
    Position Sensor returns a numpy array containing the position x, y and the
    orientation of the anchor.
    """

    def _compute_raw_sensor(self):
        self._values = np.asarray((*self._anchor.position, self._anchor.angle))

    def _apply_normalization(self):

        assert self._playground

        if self._playground.size:
            self._values /= (
                self._playground.size[0],
                self._playground.size[1],
                2 * math.pi,
            )

    @property
    def shape(self):
        return (3, 1)


class Velocity(InternalSensor):
    def _compute_raw_sensor(self):
        self._values = np.asarray(
            (*self._anchor.velocity, self._anchor.angular_velocity)
        )

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3, 1)


class RelativeVelocity(InternalSensor):
    def _compute_raw_sensor(self):

        vel = self._anchor.velocity.rotated(-self._anchor.angle)

        self._values = np.asarray((*vel, self._anchor.angular_velocity))

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3, 1)


class Time(InternalSensor):
    def _compute_raw_sensor(self):
        self._values = np.array(self.playground.timestep)

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (1, 1)
