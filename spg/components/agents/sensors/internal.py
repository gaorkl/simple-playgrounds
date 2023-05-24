import numpy as np
from gymnasium import spaces

from spg.core.entity.sensor import SensorMixin


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

