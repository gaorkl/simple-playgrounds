import numpy as np
from gymnasium import spaces

from spg.core.entity.interaction.sensor import SensorMixin

##################
# Internal Sensors
##################


class Position(SensorMixin):
    @property
    def observation(self):
        return self.position

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(2,), dtype=np.float32)


class BasePosition(Position):
    @property
    def observation(self):
        return self.base.position


class Velocity(SensorMixin):
    @property
    def observation(self):
        return self.velocity

    @property
    def observation_space(self):
        return spaces.Box(-np.inf, np.inf, shape=(2,), dtype=np.float32)


class RelativeVelocity(Velocity):
    @property
    def observation(self):

        if self.anchor is None:
            return self.velocity

        return self.velocity.rotated(-self.base.angle)
