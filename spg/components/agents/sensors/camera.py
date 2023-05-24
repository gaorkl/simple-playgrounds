from __future__ import annotations

import numpy as np
from gymnasium import spaces

from spg.core.sensor.ray.ray import RaySensor


class RGBCamera(RaySensor):
    @property
    def observation_space(self):
        return spaces.Box(low=0, high=255, shape=(self.resolution, 3))

    def _convert_hitpoints_to_observation(self):
        self._observation = self._hitpoints[:, 10:13]

    def _get_ray_colors(self):
        return self._observation.astype(np.uint8)


class GreyCamera(RaySensor):
    @property
    def observation_space(self):
        return spaces.Box(low=0, high=255, shape=(self.resolution,))

    def _convert_hitpoints_to_observation(self):
        rbg = self._hitpoints[:, 10:13]
        self._observation = np.dot(rbg, [0.299, 0.587, 0.114])

    def _get_ray_colors(self):
        grey = np.dot(self._observation, [0.299, 0.587, 0.114]).astype(np.uint8)
        return np.stack([grey, grey, grey], axis=1)
