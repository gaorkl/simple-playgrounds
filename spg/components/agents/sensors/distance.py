from __future__ import annotations

import numpy as np
from gymnasium import spaces

from spg.core.sensor.ray.ray import RaySensor


class Distance(RaySensor):

    @property
    def observation_space(self):
        return spaces.Box(low=0, high=self.max_range, shape=(self.resolution,))

    def _convert_hitpoints_to_observation(self):
        self._observation = self._hitpoints[:, 9]

    def _get_ray_colors(self):
        dist = (1 - self._observation / self.max_range) * 255
        dist = dist.astype(np.uint8)
        return np.stack([dist, dist, dist], axis=1)
