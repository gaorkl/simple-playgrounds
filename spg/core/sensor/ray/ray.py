from __future__ import annotations

from abc import abstractmethod
from collections import namedtuple
from typing import TYPE_CHECKING, List, Optional, Union

import arcade
import numpy as np

from spg.core.entity.sensor import SensorMixin

if TYPE_CHECKING:
    from spg.core.entity import Entity
    from spg.core.playground import Playground


Detection = namedtuple("Detection", "entity, distance, angle")

# View Pos 2, Abs Env Position 2, Rel Position 2, Sensor center on view 2, ID 1, Distance 1, Color 3
SIZE_OUTPUT_BUFFER = 13


class RaySensor(SensorMixin):
    """
    Base class for Ray Based sensors.
    Ray sensors use Arcade shaders
    """

    angle: float
    playground: Playground

    def __init__(
        self,
        fov: float,
        resolution: int,
        max_range: float,
        invisible_entities: Optional[Union[List[Entity], Entity]] = None,
        spatial_resolution: float = 1,
        **kwargs,
    ):

        super().__init__(**kwargs)

        # Sensor characteristics
        self.spatial_resolution = spatial_resolution
        self.fov = fov
        self.resolution = resolution
        self.max_range = max_range

        self.n_points = int(max_range / spatial_resolution)
        self.fov = fov

        if self.resolution < 0:
            raise ValueError("resolution must be more than 1")
        if self.fov < 0:
            raise ValueError("field of view must be more than 1")
        if self.max_range < 0:
            raise ValueError("range must be more than 1")

        # Invisible elements
        invisible_entities = (
            []
            if not invisible_entities
            else [invisible_entities]
            if isinstance(invisible_entities, Entity)
            else invisible_entities
        )

        for ent in invisible_entities:
            self.add_invisible_entity(ent)

        self._invisible_entities: List[Entity] = []

        self._hitpoints = np.zeros((self.resolution, SIZE_OUTPUT_BUFFER))
        self._observation = self.observation_space.sample() * 0
        self.updated = False

        self.invisible_changed = False

    def add_invisible_entity(self, *entities: Entity):

        for ent in entities:
            self._invisible_entities.append(ent)

        self.invisible_changed = True

    def remove_invisible_entity(self, *entities: Entity):

        for ent in entities:
            self._invisible_entities.remove(ent)

        self.invisible_changed = True

    @property
    def invisible_ids(self):
        return [ent.uid for ent in self._invisible_entities]

    @property
    def invisible_entities(self):
        return self._invisible_entities

    @abstractmethod
    def _get_ray_colors(self):
        ...

    def draw(self):
        view_xy = self._hitpoints[:, :2]
        center_xy = self._hitpoints[:, 6:8]
        color = self._get_ray_colors()

        for ind_pt in range(len(view_xy)):

            if self._hitpoints[ind_pt, 8] == 0:
                continue
            color_pt = color[ind_pt]
            arcade.draw_line(
                center_xy[ind_pt, 0],
                center_xy[ind_pt, 1],
                view_xy[ind_pt, 0],
                view_xy[ind_pt, 1],
                color_pt,
            )

    @property
    def end_positions(self):
        angles = np.array(
            [
                self.angle - self.fov / 2 + i_ray * self.fov / (self.resolution - 1)
                for i_ray in range(self.resolution)
            ]
        )
        x = self.max_range * np.cos(angles)
        y = self.max_range * np.sin(angles)
        return np.vstack((x, y))

    def pre_step(self):
        self.updated = False
        self._observation *= 0

    def update_observations(self, hitpoints: np.ndarray):
        """
        Update the observations of the sensor.
        Hitpoints are the points where the rays hit something.
        They are of size 13 composed of the following information:
        - View Pos 2
        - Abs Env Position 2
        - Rel Position 2
        - Sensor center on view 2
        - ID 1
        - Distance 1
        - Color 3
        """

        self._hitpoints = hitpoints
        self._observation = self._convert_hitpoints_to_observation()
        self.updated = True

    @abstractmethod
    def _convert_hitpoints_to_observation(self):
        ...

    @property
    def observation(self):
        return self._observation
