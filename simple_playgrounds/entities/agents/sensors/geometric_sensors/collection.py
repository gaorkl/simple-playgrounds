"""
Lidar Sensors provide the Entities detected by rays or cones, as well as their distance,
and angle of the ray or cone.
"""
import math
import numpy
from abc import ABC
import cv2

import pymunk

from simple_playgrounds.entities.agents.sensors.geometric_sensors.geometric_sensor import GeometricSensor


class DistanceRays(GeometricSensor, ABC):
    """
    DistanceRays are Sensors that measure distances by rays.
    """
    sensor_type = 'distance-rays'

    def __init__(self, anchor, invisible_elements=None, **sensor_params):
        """
        Args:
            anchor: Entity on which the sensor is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            **sensor_params: Additional Parameters.

        Keyword Args:
            resolution: number of rays evenly spaced across the field of view.
            fov: field of view
            range: range of the rays.
        """
        default_config = self._parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        # Field of View of the Sensor
        self.radius_beam = 1

        if self._resolution == 1:
            self.angles = [0]
        else:
            self.angles = [n * self._fov / (self._resolution - 1) - self._fov / 2 for n in range(self._resolution)]

        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sensor_value = numpy.zeros(self.shape)

        self.invisible_shapes = []
        for entity in self.invisible_elements:
            self.invisible_shapes += [entity.pm_visible_shape, entity.pm_interaction_shape]
        self.invisible_shapes = list(set(self.invisible_shapes))
        if None in self.invisible_shapes:
            self.invisible_shapes.remove(None)

    def _compute_collisions(self, playground, sensor_angle):

        position = self.anchor.pm_body.position
        angle = self.anchor.pm_body.angle + sensor_angle

        position_end = (position[0] + self.range * math.cos(angle),
                        position[1] + self.range * math.sin(angle)
                        )

        collisions = playground.space.segment_query(position, position_end, 0, self.filter)

        # remove invisibles
        distances = [col.alpha for col in collisions
                      if col.shape not in self.invisible_shapes and col.shape.sensor != True]

        # if len(distances) > 1 : print(distances)

        return min(distances, default=1) * self.range

    def compute_raw_sensor(self, pg):

        for index, sensor_angle in enumerate(self.angles):

            dist = self._compute_collisions(pg, sensor_angle)

            self.sensor_value[index] = dist


class TouchSensor(DistanceRays):

    sensor_type = 'touch'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **sensor_params):
        """
        Args:
            anchor: Entity on which the Lidar is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            **sensor_params: Additional Parameters.

        Keyword Args:
            resolution: number of rays evenly spaced across the field of view.
            fov: field of view
            range: range of the rays.
        """
        default_config = self._parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        self.normalize = normalize
        self.range = self.anchor.radius + self.range

    def compute_raw_sensor(self, pg):

        super().compute_raw_sensor(pg)

        self.sensor_value = self.sensor_value - self.anchor.radius + 2
        self.sensor_value[ self.sensor_value<0] = 0
        self.sensor_value = self.range - self.anchor.radius + 2 - self.sensor_value

    def apply_normalization(self):
        self.sensor_value = self.sensor_value / (self.range - self.anchor.radius + 2)

    def draw(self, width_display, height_sensor):

        expanded = numpy.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = numpy.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False:
            # img = (img - self.anchor.radius) / (self._range - self.anchor.radius)
            img = img / (self.range - self.anchor.radius + 2)

        return img


class DepthSensor(DistanceRays):

    sensor_type = 'depth'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **sensor_params):
        """
        Args:
            anchor: Entity on which the sensor is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            **sensor_params: Additional Parameters.

        Keyword Args:
            resolution: number of rays evenly spaced across the field of view.
            fov: field of view
            range: range of the rays.
        """
        default_config = self._parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        self.normalize = normalize

    def apply_normalization(self):

        self.sensor_value = self.sensor_value / self.range

    def draw(self, width_display, height_sensor):

        expanded = numpy.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = numpy.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False:
            img = img / (self.range)

        return img


class ProximitySensor(DistanceRays):

    sensor_type = 'proximity'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **sensor_params):
        """
        Args:
            anchor: Entity on which the sensor is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            **sensor_params: Additional Parameters.

        Keyword Args:
            resolution: number of rays evenly spaced across the field of view.
            fov: field of view
            range: range of the rays.
        """
        default_config = self._parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        self.normalize = normalize

    def compute_raw_sensor(self, pg):

        super().compute_raw_sensor(pg)

        self.sensor_value = self.range - self.sensor_value

    def apply_normalization(self):
        self.sensor_value = self.sensor_value / self.range

    def draw(self, width_display, height_sensor):

        expanded = numpy.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = numpy.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False:
            # img = (img - self.anchor.radius) / (self._range - self.anchor.radius)
            img = img / (self.range)

        return img

