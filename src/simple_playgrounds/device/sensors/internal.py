""" Module implementing robotic sensors: Cameras, Lidar, touch sensing.

These sensors are very close to physical sensors that could be used on real robots.
These sensors can be noisy.
Importantly, as Simple-Playgrounds is a 2D environments, these sensors are 1D.
"""
import math
import numpy as np

from simple_playgrounds.device.sensor import InternalSensor


class Position(InternalSensor):

    """
    Position Sensor returns a numpy array containing the position x, y and the
    orientation of the anchor.
    """

    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.position),
                                             [self._anchor.angle]])

    def set_playground_size(self, size):
        self._pg_size = size

    def _apply_normalization(self):
        self.sensor_values /= (self._pg_size[0], self._pg_size[1], 2*math.pi)

    @property
    def shape(self):
        return (3,)


class Velocity(InternalSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.velocity),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3,)


class RelativeVelocity(InternalSensor):
    def _compute_raw_sensor(self, playground, *_):

        vel = self._anchor.velocity.rotated(-self._anchor.angle)

        self.sensor_values = np.concatenate([np.array(vel),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3,)


class Time(InternalSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.array(playground._timestep)

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (1,)
