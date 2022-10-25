from __future__ import annotations

from abc import ABC
from array import array
from os import path
from typing import TYPE_CHECKING, List

import arcade
import numpy as np

from ...utils.uid import id_to_pixel
from ...view import TopDownView
from .sensor import ExternalSensor

if TYPE_CHECKING:
    from ...playground import Playground


class RayCompute:
    def __init__(self, playground: Playground, size, center, zoom, use_shader=True):

        self._playground = playground
        self.ctx = playground.window.ctx

        self._use_shader = use_shader

        self._id_view = TopDownView(
            playground,
            size,
            center,
            zoom,
            display_uid=True,
            draw_interactive=False,
            draw_transparent=False,
            draw_zone=False,
        )
        self._color_view = TopDownView(
            playground,
            size,
            center,
            zoom,
            draw_interactive=False,
            draw_transparent=False,
            draw_zone=False,
        )

        self._sensors: List[RaySensor] = []

        if self._use_shader:

            self._view_params_buffer = self.ctx.buffer(
                data=array(
                    "f",
                    [
                        self._id_view.center[0],
                        self._id_view.center[1],
                        self._id_view.width,
                        self._id_view.height,
                        self._id_view.zoom,
                    ],
                )
            )

            self._view_params_buffer.bind_to_storage_buffer(binding=6)

            self._position_buffer = None
            self._param_buffer = None
            self._output_rays_buffer = None
            self._inv_buffer = None

            shader_dir = path.abspath(path.join(__file__, "../shaders"))

            with open(shader_dir + "/id_compute.glsl", "rt", encoding="utf-8") as f_id:
                self._source_compute_ids = f_id.read()

            with open(
                shader_dir + "/color_compute.glsl", "rt", encoding="utf-8"
            ) as f_col:
                self._source_compute_colors = f_col.read()

            self._id_shader = None
            self._color_shader = None

    @property
    def _n_sensors(self):
        return len(self._sensors)

    @property
    def _max_n_rays(self):
        return max(sensor.resolution for sensor in self._sensors)

    @property
    def _max_invisible(self):
        return 1 + max(len(sensor.invisible_ids) for sensor in self._sensors)

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

        for sensor in self._sensors:
            yield sensor.max_range
            yield sensor.fov
            yield sensor.resolution
            yield sensor.n_points

    def _generate_position_buffer(self):

        for sensor in self._sensors:
            yield sensor.position[0]
            yield sensor.position[1]
            yield sensor.angle

    def _generate_output_buffer(self):

        for _ in range(self._n_sensors):
            for _ in range(self._max_n_rays):

                # View Position
                yield 0.0
                yield 0.0

                # Abs Env Position
                yield 0.0
                yield 0.0

                # Rel Position
                yield 0.0
                yield 0.0

                # Sensor center on view
                yield 0.0
                yield 0.0

                # ID
                yield 0.0

                # Distance
                yield 0.0

                # Color
                yield 0.0
                yield 0.0
                yield 0.0

    def _generate_invisible_buffer(self):

        for sensor in self._sensors:

            count = 1
            yield sensor.anchor.uid

            for inv in sensor.invisible_ids:
                yield inv
                count += 1

            while count < self._max_invisible:
                yield 0
                count += 1

    def _generate_shaders(self):
        new_source = self._source_compute_ids
        new_source = new_source.replace("N_SENSORS", str(len(self._sensors)))
        new_source = new_source.replace("MAX_N_RAYS", str(self._max_n_rays))
        new_source = new_source.replace("MAX_N_INVISIBLE", str(self._max_invisible))
        id_shader = self.ctx.compute_shader(source=new_source)

        new_source = self._source_compute_colors
        new_source = new_source.replace("MAX_N_RAYS", str(self._max_n_rays))
        color_shader = self.ctx.compute_shader(source=new_source)

        return id_shader, color_shader

    def add(self, sensor):
        self._sensors.append(sensor)

        if self._use_shader:
            self._update_buffers_and_shaders()

    def _update_buffers_and_shaders(self):
        (
            self._position_buffer,
            self._param_buffer,
            self._output_rays_buffer,
            self._inv_buffer,
        ) = self._generate_buffers()

        self._id_shader, self._color_shader = self._generate_shaders()

    def update_sensors(self):

        if not self._sensors:
            return

        self._id_view.update(force=True)
        self._color_view.update(force=True)

        if self._use_shader:
            self._update_sensors_shaders()

        else:
            self._update_sensors_cpu()

    def _update_sensors_shaders(self):

        update_inv = False
        for sensor in self._sensors:
            if sensor.require_invisible_update:
                update_inv = True

        if update_inv:
            self._update_buffers_and_shaders()

        self._position_buffer = self.ctx.buffer(
            data=array("f", self._generate_position_buffer())
        )
        self._position_buffer.bind_to_storage_buffer(binding=3)

        self._id_view.texture.use()
        self._id_shader.run(group_x=self._n_sensors)

        self._color_view.texture.use()
        self._color_shader.run(group_x=self._n_sensors)

        hitpoints = np.frombuffer(
            self._output_rays_buffer.read(), dtype=np.float32
        ).reshape(self._n_sensors, self._max_n_rays, 13)

        for index, sensor in enumerate(self._sensors):
            sensor.update_hitpoints(hitpoints[index, : sensor.resolution, :])

    def _update_sensors_cpu(self):

        img_color = self._color_view.get_np_img()
        img_id = self._id_view.get_np_img()

        for sensor in self._sensors:

            end_positions = sensor.end_positions

            ray_start_x = (
                sensor.position[0] - self._id_view.center[0]
            ) * self._id_view.zoom + self._id_view.width / 2
            ray_start_y = (
                sensor.position[1] - self._id_view.center[1]
            ) * self._id_view.zoom + self._id_view.height / 2

            center_on_view = np.asarray((ray_start_x, ray_start_y)).reshape(2, 1)

            rays_end = center_on_view + end_positions * self._id_view.zoom

            points = np.linspace(center_on_view, rays_end, num=sensor.n_points)

            points[:, 0, :] = (points[:, 0, :] > 0) * points[:, 0, :]
            points[:, 0, :] = (points[:, 0, :] < self._id_view.width) * points[
                :, 0, :
            ] + (points[:, 0, :] >= self._id_view.width) * (self._id_view.width - 1)

            points[:, 1, :] = (points[:, 1, :] > 0) * points[:, 1, :]
            points[:, 1, :] = (points[:, 1, :] < self._id_view.height) * points[
                :, 1, :
            ] + (points[:, 1, :] >= self._id_view.height) * (self._id_view.height - 1)

            points = points.swapaxes(1, 2).reshape(-1, 2)

            rr, cc = points[:, 1].astype(np.int), points[:, 0].astype(np.int)

            # Get Ids
            pts = img_id[rr, cc]

            ids = 256 * 256 * pts[:, 2] + 256 * pts[:, 1] + pts[:, 0]

            #  remove invisible
            for inv in sensor.invisible_ids:
                ids = (ids != inv) * ids

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
                view_position[:, 0] - self._id_view.width / 2
            ) / self._id_view.zoom + self._id_view.center[0]

            y_abs = (
                view_position[:, 1] - self._id_view.height / 2
            ) / self._id_view.zoom + self._id_view.center[1]

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

            sensor.update_hitpoints(hitpoints)


class RaySensor(ExternalSensor, ABC):
    """
    Base class for Ray Based sensors.
    Ray sensors use Arcade shaders
    """

    def __init__(
        self,
        spatial_resolution: float = 1,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self._spatial_resolution = spatial_resolution
        self._n_points = int(self._range / self._spatial_resolution)

        self._hitpoints = 0

    @property
    def spatial_resolution(self):
        return self._spatial_resolution

    @property
    def n_points(self):
        return self._n_points

    def update_hitpoints(self, hitpoints):
        self._hitpoints = hitpoints

    @property
    def end_positions(self):
        angles = np.array(
            [
                self.angle - self.fov / 2 + i_ray * self.fov / (self._resolution - 1)
                for i_ray in range(self._resolution)
            ]
        )
        x = self._range * np.cos(angles)
        y = self._range * np.sin(angles)
        return np.vstack((x, y))


class DistanceSensor(RaySensor):
    def _compute_raw_sensor(self):
        self._values = self._hitpoints[:, 9]

    def draw(self):

        if self._disabled:
            return
        view_xy = self._hitpoints[:, :2]
        center_xy = self._hitpoints[:, 6:8]
        dist = 1 - self._hitpoints[:, 9] / self._range

        for ind_pt in range(len(view_xy)):

            color = (
                int(dist[ind_pt] * 255),
                int(dist[ind_pt] * 255),
                int(dist[ind_pt] * 255),
            )
            arcade.draw_line(
                center_xy[ind_pt, 0],
                center_xy[ind_pt, 1],
                view_xy[ind_pt, 0],
                view_xy[ind_pt, 1],
                color,
            )

    @property
    def shape(self):
        return self._resolution, 1

    @property
    def _default_value(self):
        return np.zeros(self.shape)

    def _apply_normalization(self):
        self._values = self._values / self._range


class RGBSensor(RaySensor):
    def _compute_raw_sensor(self):
        self._values = self._hitpoints[:, 10:13]

    def draw(self):
        if self._disabled:
            return
        view_xy = self._hitpoints[:, :2]
        center_xy = self._hitpoints[:, 6:8]
        color = self._hitpoints[:, 10:13].astype(np.uint8)

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
    def shape(self):
        return self._resolution, 3

    @property
    def _default_value(self):
        return np.zeros(self.shape)

    def _apply_normalization(self):
        self._values = self._values / 255.0


class SemanticSensor(RaySensor):
    def _compute_raw_sensor(self):
        self._values = self._hitpoints[:, 8:10]

    def draw(self):

        if self._disabled:
            return

        view_xy = self._hitpoints[:, :2]
        center_xy = self._hitpoints[:, 6:8]
        id_detection = self._hitpoints[:, 8].astype(np.int)

        for ind_pt in range(len(view_xy)):

            if id_detection[ind_pt] != 0:

                color = id_to_pixel(id_detection[ind_pt])

                arcade.draw_line(
                    center_xy[ind_pt, 0],
                    center_xy[ind_pt, 1],
                    view_xy[ind_pt, 0],
                    view_xy[ind_pt, 1],
                    color,
                )

    @property
    def shape(self):
        return self._resolution, 2

    @property
    def _default_value(self):
        return np.zeros(self.shape)

    def _apply_normalization(self):
        self._values = self._values / (1, self._range)
