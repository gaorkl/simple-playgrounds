from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from gym import spaces

from spg.core.sensor.ray.ray import RaySensor

UID = spaces.Box(low=0, high=255 + 255**2 + 255**3, shape=(1,), dtype=np.uint32)
DISTANCE = spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32)
RELATIVE_POSITION = spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)


class Semantic(RaySensor, ABC):

    def _convert_hitpoints_to_observation(self):
        id_rgb = self._hitpoints[:, 8:10]
        uids = np.dot(id_rgb, [1, 255, 255**2]).astype(np.uint32)
        uids = np.unique(uids)

        entities = [self.playground.uids_to_entities[uid] for uid in uids]
        self._observation = self._extract_semantic(entities)

    @abstractmethod
    def _extract_semantic(self, entities):
        pass

    def _get_ray_colors(self):
        return self._hitpoints[:, 8:10].astype(np.uint8)


class SemanticID(Semantic):

    @property
    def observation_space(self):
        return spaces.Sequence(spaces.Box(low=0, high=255 + 255**2 + 255**3))

    def _extract_semantic(self, entities):
        return [entity.uid for entity in entities]
