from __future__ import annotations

from abc import ABC, abstractmethod
from array import array
from os import path
from typing import List, TYPE_CHECKING

import numpy as np

from spg.core.sensor.ray.ray import SIZE_OUTPUT_BUFFER

if TYPE_CHECKING:
    from spg.core.playground import Playground
    from spg.core.sensor import RaySensor


class RayComputeStrategy(ABC):

    @abstractmethod
    def __init__(self, ray_compute: RayCompute):

        self._ray_compute = ray_compute

    @property
    def ctx(self):
        return self._ray_compute.ctx

    @property
    def id_view(self):
        return self._ray_compute.id_view

    @property
    def color_view(self):
        return self._ray_compute.color_view

    @property
    def playground(self):
        return self._ray_compute.playground

    @property
    def sensors(self):
        return self._ray_compute.sensors

    @property
    def max_n_rays(self):
        return self._ray_compute.max_n_rays

    @property
    def max_invisible(self):
        return self._ray_compute.max_invisible

    @abstractmethod
    def compute(self):
        pass


class ShaderCompute(RayComputeStrategy):

    def __init__(self, ray_compute: RayCompute):

        super().__init__(ray_compute)

        self._view_params_buffer = self.ctx.buffer(
            data=array(
                "f",
                [
                    self.id_view.center[0],
                    self.id_view.center[1],
                    self.id_view.width,
                    self.id_view.height,
                    self.id_view.scale,
                ],
            )
        )

        self._view_params_buffer.bind_to_storage_buffer(binding=6)

        self._position_buffer = None
        self._param_buffer = None
        self._output_rays_buffer = None
        self._inv_buffer = None

        shader_dir = path.abspath(path.join(__file__, "../"))

        with open(shader_dir + "/id_compute.glsl", "rt", encoding="utf-8") as f_id:
            self._source_compute_ids = f_id.read()

        with open(
            shader_dir + "/color_compute.glsl", "rt", encoding="utf-8"
        ) as f_col:
            self._source_compute_colors = f_col.read()

        self._id_shader = None
        self._color_shader = None

    def _generate_buffers(self):

        position_buffer = self.ctx.buffer(
            data=array("f", self._generate_position_buffer())
        )
        param_buffer = self.ctx.buffer(
            data=array("f", self._generate_parameter_buffer())
        )
        output_rays_buffer = self.ctx.buffer(
            data=array("f", self._generate_output_buffer())
        )
        inv_buffer = self.ctx.buffer(data=array("I", self._generate_invisible_buffer()))

        param_buffer.bind_to_storage_buffer(binding=2)
        position_buffer.bind_to_storage_buffer(binding=3)
        output_rays_buffer.bind_to_storage_buffer(binding=4)
        inv_buffer.bind_to_storage_buffer(binding=5)

        return position_buffer, param_buffer, output_rays_buffer, inv_buffer

    def _generate_parameter_buffer(self):

        for sensor in self.sensors:
            yield sensor.max_range
            yield sensor.fov
            yield sensor.resolution
            yield sensor.n_points

    def _generate_position_buffer(self):

        for sensor in self.sensors:
            yield sensor.position[0]
            yield sensor.position[1]
            yield sensor.angle

    def _generate_output_buffer(self):

        for _ in range(len(self.sensors)):
            for _ in range(self.max_n_rays):

                for _ in range(SIZE_OUTPUT_BUFFER):
                    yield 0.0

    def _generate_invisible_buffer(self):


        for sensor in self.sensors:

            count = 1
            yield sensor.anchor.uid

            for inv in sensor.invisible_ids:
                yield inv
                count += 1

            while count < self.max_invisible:
                yield 0
                count += 1

    def _generate_shaders(self):
        new_source = self._source_compute_ids
        new_source = new_source.replace("N_SENSORS", str(len(self.sensors)))
        new_source = new_source.replace("MAX_N_RAYS", str(self.max_n_rays))
        new_source = new_source.replace("MAX_N_INVISIBLE", str(self.max_invisible))
        id_shader = self.ctx.compute_shader(source=new_source)

        new_source = self._source_compute_colors
        new_source = new_source.replace("MAX_N_RAYS", str(self.max_n_rays))
        color_shader = self.ctx.compute_shader(source=new_source)

        return id_shader, color_shader

    def update_buffers_and_shaders(self):
        (
            self._position_buffer,
            self._param_buffer,
            self._output_rays_buffer,
            self._inv_buffer,
        ) = self._generate_buffers()

        self._id_shader, self._color_shader = self._generate_shaders()

    def compute(self):

        requires_buffer_update = False

        # check if invisible list changed in any of sensors
        for sensor in self.sensors:
            if sensor.invisible_changed:
                requires_buffer_update = True
                break

        if requires_buffer_update:
            self.update_buffers_and_shaders()

        for sensor in self.sensors:
            sensor.invisible_changed = False

        self._position_buffer = self.ctx.buffer(
            data=array("f", self._generate_position_buffer())
        )
        self._position_buffer.bind_to_storage_buffer(binding=3)

        self.id_view.texture.use()
        self._id_shader.run(group_x=len(self.sensors))

        self.color_view.texture.use()
        self._color_shader.run(group_x=len(self.sensors))

        hitpoints = np.frombuffer(
            self._output_rays_buffer.read(), dtype=np.float32
        ).reshape((len(self.sensors), self.max_n_rays, SIZE_OUTPUT_BUFFER))

        for index, sensor in enumerate(self.sensors):
            sensor.update_observations(hitpoints[index, : sensor.resolution, :])


class NumpyCompute(RayComputeStrategy):

    def __init__(self, ray_compute: RayCompute):
        super().__init__(ray_compute)

    def compute(self):

        img_color = self.color_view.get_np_img()
        img_id = self.id_view.get_np_img()

        for sensor in self.sensors:

            end_positions = sensor.end_positions

            ray_start_x = (
                                  sensor.position[0] - self.id_view.center[0]
                          ) * self.id_view.scale+ self.id_view.width / 2
            ray_start_y = (
                                  sensor.position[1] - self.id_view.center[1]
                          ) * self.id_view.scale + self.id_view.height / 2

            center_on_view = np.asarray((ray_start_x, ray_start_y)).reshape(2, 1)

            rays_end = center_on_view + end_positions * self.id_view.scale

            points = np.linspace(center_on_view, rays_end, num=sensor.n_points)

            points[:, 0, :] = (points[:, 0, :] > 0) * points[:, 0, :]
            points[:, 0, :] = (points[:, 0, :] < self.id_view.width) * points[
                                                                        :, 0, :
                                                                        ] + (
                                          points[:, 0, :] >= self.id_view.width) * (self.id_view.width - 1)

            points[:, 1, :] = (points[:, 1, :] > 0) * points[:, 1, :]
            points[:, 1, :] = (points[:, 1, :] < self.id_view.height) * points[
                                                                         :, 1, :
                                                                         ] + (
                                          points[:, 1, :] >= self.id_view.height) * (self.id_view.height - 1)

            points = points.swapaxes(1, 2).reshape(-1, 2)

            rr, cc = points[:, 1].astype(np.int), points[:, 0].astype(np.int)

            # Get Ids
            pts = img_id[rr, cc]

            ids = 256 * 256 * pts[:, 2] + 256 * pts[:, 1] + pts[:, 0]

            #  remove invisible
            for inv in sensor.invisible_ids:
                ids *= (ids != inv)

            ids = ids.reshape(-1, sensor.resolution).transpose()

            # take index and value of first non-zero
            index_first_non_zero = np.argmax((ids != 0), axis=1)

            # Calculate hitpoints
            id_first_non_zero = ids[
                np.arange(len(index_first_non_zero)), index_first_non_zero
            ]

            points = points.reshape((-1, sensor.resolution, 2))
            view_position = points[
                            index_first_non_zero, np.arange(len(index_first_non_zero)), :
                            ]

            color = img_color[
                view_position[:, 1].astype(np.int), view_position[:, 0].astype(np.int)
            ]
            color[id_first_non_zero == 0] = (0, 0, 0)

            # Relative pos and distance
            rel_pos = center_on_view.transpose() - view_position
            distance = np.sqrt(rel_pos[:, 0] ** 2 + rel_pos[:, 1] ** 2)
            distance[id_first_non_zero == 0] = sensor.max_range
            distance = np.expand_dims(distance, -1)

            x_abs = (
                            view_position[:, 0] - self.id_view.width / 2
                    ) / self.id_view.scale + self.id_view.center[0]

            y_abs = (
                            view_position[:, 1] - self.id_view.height / 2
                    ) / self.id_view.scale + self.id_view.center[1]

            view_position[id_first_non_zero == 0, :] = rays_end[
                                                       :, id_first_non_zero == 0
                                                       ].transpose()
            abs_env_position = np.vstack((x_abs, y_abs)).transpose()

            center_on_view = np.broadcast_to(
                center_on_view.transpose(), (sensor.resolution, 2)
            )

            id_first_non_zero = np.expand_dims(id_first_non_zero, -1)

            hitpoints = np.hstack(
                (
                    view_position,
                    abs_env_position,
                    np.zeros((sensor.resolution, 2)),
                    center_on_view,
                    id_first_non_zero,
                    distance,
                    color,
                )
            )

            sensor.update_observations(hitpoints)


class RayCompute:

    def __init__(self, playground: Playground, scale=1, use_shader=True):

        self.playground = playground
        self.ctx = playground.window.ctx

        # Check if OPengl version allows shaders to be used
        if not self.ctx.gl_version >= (4, 3):
            use_shader = False

        self.sensors: List[RaySensor] = []

        if use_shader:
            self._compute_strategy = ShaderCompute(self)
        else:
            self._compute_strategy = NumpyCompute(self)

        self.use_shader = use_shader

    @property
    def id_view(self):
        return self.playground.id_view

    @property
    def color_view(self):
        return self.playground.color_view

    @property
    def max_n_rays(self):
        return max(sensor.resolution for sensor in self.sensors)

    @property
    def max_invisible(self):
        return 1 + max(len(sensor.invisible_ids) for sensor in self.sensors)

    def add(self, sensor):
        self.sensors.append(sensor)

        if isinstance(self._compute_strategy, ShaderCompute):
            self._compute_strategy.update_buffers_and_shaders()

    def update_sensors(self):

        if not self.sensors:
            return

        self._compute_strategy.compute()
