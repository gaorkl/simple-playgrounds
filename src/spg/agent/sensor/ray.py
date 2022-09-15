from abc import ABC
from array import array
from os import path
from typing import TYPE_CHECKING, List

import numpy as np

if TYPE_CHECKING:
    from ...playground import Playground

from ...view import TopDownView
from .sensor import ExternalSensor


class RayShader:

    def __init__(self, playground: Playground, size, center, zoom):

        self._playground = playground
        self.ctx = playground.window.ctx

        self.id_view = TopDownView(
            playground, size, center, zoom, display_uid=True, draw_interactive=False, draw_transparent=False)
        self.color_view = TopDownView(
            playground, size, center, zoom, draw_interactive=True, draw_transparent=True)

        self._sensors: List[RaySensor] = []

        self.view_params_buffer = self.ctx.buffer(data=array('f',
                                                             [self.id_view.center[0],
                                                              self.id_view.center[1],
                                                              self.id_view.width,
                                                              self.id_view.height,
                                                              self.id_view.zoom
                                                              ]))

        shader_dir = path.abspath(path.join(__file__, 'shaders'))

        with open(shader_dir + 'id_compute.glsl') as f:
            self.source_compute_ids = f.read()

        with open(shader_dir + 'color_compute.glsl') as f:
            self.source_compute_colors = f.read()

    @property
    def _n_sensors(self):
        return len(self._sensors)

    @property
    def _max_n_rays(self):
        return max(sensor.n_rays for sensor in self.sensors)

    @property
    def _max_invisible(self):
        return 1 + max(len(sensor.invisible_ids) for sensor in self.sensors)

    def generate_parameter_buffer(self):

        for sensor in self._sensors:
            yield sensor.range
            yield sensor.fov
            yield sensor.n_rays
            yield sensor.n_points

    def generate_position_buffer(self):

        for sensor in self._sensors:
            yield sensor.center[0]
            yield sensor.center[1]
            yield sensor.angle

    def generate_output_buffer(self):

        for _ in range(self._n_sensors):
            for _ in range(self._max_n_rays):

                # View Position
                yield 0.
                yield 0.

                # Abs Env Position
                yield 0.
                yield 0.

                # Rel Position
                yield 0.
                yield 0.

                # Sensor center on view
                yield 0.
                yield 0.

                # ID
                yield 0.

                # Distance
                yield 0.

                # Color
                yield 0.
                yield 0.
                yield 0.

    def generate_invisible_buffer(self):

        for sensor in self._sensors:

            count = 1
            yield sensor.anchor.id

            for inv in sensor.invisible_ids:
                yield inv
                count += 1

            while count < self._max_invisible - 1:
                yield 0
                count += 1

    def add(self, sensor):
        self._sensors.append(sensor)

        self.position_buffer = self.ctx.buffer(
            data=array('f', self.generate_position_buffer()))
        self.param_buffer = self.ctx.buffer(
            data=array('f', self.generate_parameter_buffer()))
        self.output_rays_buffer = self.ctx.buffer(
            data=array('f', self.generate_output_buffer()))
        self.inv_buffer = self.ctx.buffer(
            data=array('I', self.generate_invisible_buffer()))

        new_source = self.source_compute_ids
        new_source = new_source.replace('N_SENSORS', str(len(self.sensors)))
        new_source = new_source.replace('MAX_N_RAYS', str(self.max_n_rays))
        new_source = new_source.replace(
            'MAX_N_INVISIBLE', str(self.max_invisible))
        self.hitpoints_shader = self.ctx.compute_shader(source=new_source)

        new_source = self.source_compute_colors
        new_source = new_source.replace('MAX_N_RAYS', str(self.max_n_rays))
        self.color_shader = self.ctx.compute_shader(source=new_source)

        self.output_rays_buffer.bind_to_storage_buffer(binding=4)
        self.param_buffer.bind_to_storage_buffer(binding=2)
        self.inv_buffer.bind_to_storage_buffer(binding=5)
        self.view_params_buffer.bind_to_storage_buffer(binding=6)

    def update_sensor(self):

        self.id_view.buf_update()
        self.color_view.buf_update()

        if self.sensors:
            self.position_buffer = self.ctx.buffer(
                data=array('f', self.generate_position_buffer()))
            self.position_buffer.bind_to_storage_buffer(binding=3)

            self.id_view.texture.use()
            self.hitpoints_shader.run(group_x=self.n_sensors)

            self.color_view.texture.use()
            self.color_shader.run(group_x=self.n_sensors)

            hitpoints = np.frombuffer(
                self.output_rays_buffer.read(),
                dtype=np.float32
            ).reshape(self.n_sensors, self.max_n_rays, 13)

            for index, sensor in enumerate(self.sensors):
                sensor.update_value(hitpoints[index, :sensor.n_rays, :])


class RaySensor(ExternalSensor, ABC):
    """
    Base class for Ray Based sensors.
    Ray sensors use Arcade shaders
    """

    def __init__(
        self,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self._hit_positions = np.zeros((self._resolution, 2))
        self._hit_values = np.zeros(self.shape)
