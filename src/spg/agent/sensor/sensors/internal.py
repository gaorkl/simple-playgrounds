""" Module implementing robotic sensors: Cameras, Lidar, touch sensing.

These sensors are very close to physical sensors that could be used on real robots.
These sensors can be noisy.
Importantly, as Simple-Playgrounds is a 2D environments, these sensors are 1D.
"""
import math
import numpy as np

from spg.agent.sensor.sensor import InternalSensor


class Position(InternalSensor):

    """
    Position Sensor returns a numpy array containing the position x, y and the
    orientation of the anchor.
    """

    def _compute_raw_sensor(self):
        self.sensor_values = np.concatenate([np.array(self._anchor.position),
                                             [self._anchor.angle]])

    def _apply_normalization(self):

        if self._playground and self.playground.size:
            self.sensor_values /= (self.playground.size[0], self.playground.size[1], 2*math.pi)

    @property
    def shape(self):
        return (3,)


class Velocity(InternalSensor):
    def _compute_raw_sensor(self):
        self.sensor_values = np.concatenate([np.array(self._anchor.velocity),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3,)


class RelativeVelocity(InternalSensor):
    def _compute_raw_sensor(self):

        vel = self._anchor.velocity.rotated(-self._anchor.angle)

        self.sensor_values = np.concatenate([np.array(vel),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3,)


class Time(InternalSensor):
    def _compute_raw_sensor(self):
        self.sensor_values = np.array(self.playground.timestep)

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (1,)
