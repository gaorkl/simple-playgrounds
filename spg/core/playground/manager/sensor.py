from __future__ import annotations

from typing import TYPE_CHECKING, List

from spg.core.view import View

if TYPE_CHECKING:
    from spg.core.entity.sensor import SensorMixin

from spg.core.sensor.ray.ray import RaySensor
from spg.core.sensor.ray.ray_compute import RayCompute


class SensorManager:
    def __init__(self, use_shader=True, sensor_scale=1, **kwargs) -> None:

        self.sensors: List[SensorMixin] = []

        self.id_view = View(
            self,
            size_on_playground=self.size,
            center=(0, 0),
            scale=sensor_scale,
            draw_transparent=False,
            uid_mode=True,
        )
        self.color_view = View(
            self,
            size_on_playground=self.size,
            center=(0, 0),
            scale=sensor_scale,
            draw_transparent=False,
        )

        self.ray_compute = RayCompute(self, use_shader)

    def update_sensors(self):

        if not self.sensors:
            return

        if not self.id_view.updated:
            self.id_view.update()

        if not self.color_view.updated:
            self.color_view.update()

        self.ray_compute.update_sensors()

    def add_sensor(self, sensor: SensorMixin):
        self.sensors.append(sensor)

        if isinstance(sensor, RaySensor):
            self.ray_compute.add(sensor)
