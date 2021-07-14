"""
This Module provides semantic sensors.
These artificial sensors return semantic information about the detected entities.
They return the actual instance of the entity detected, which allow to access their attributes.
E.g. position, velocity, mass, shape can be accessed.
"""
from typing import List, Optional, Dict, Union

import math
from operator import attrgetter

import numpy as np
from skimage.draw import line, disk

from .sensor import RayCollisionSensor
from ...common.definitions import SensorTypes, Detection
from ...configs import parse_configuration
from ...common.entity import Entity
from ..parts.parts import Part


class SemanticRay(RayCollisionSensor):
    """
    Semantic Ray detect Entities by projecting rays.
    This sensor returns the actual :Entity: object.
    All the attributes (position, physical properties, ...) of the returned
    entity can be accessed.
    """

    def __init__(self,
                 anchor: Part,
                 invisible_elements: Optional[Union[List[Entity], Entity]] = None,
                 normalize: bool = True,
                 noise_params: Optional[Dict] = None,
                 remove_duplicates: bool = True,
                 **kwargs):

        default_config = parse_configuration('agent_sensors', SensorTypes.SEMANTIC_RAY)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         remove_duplicates=remove_duplicates,
                         **kwargs)

        self._sensor_max_value = self._max_range

    def _compute_raw_sensor(self, playground, *_):

        collision_points = self._compute_points(playground)

        collision_points = {
            k: v
            for k, v in collision_points.items() if v != []
        }

        self.sensor_values = self._collisions_to_detections(
            playground, collision_points)
        # class Point just for modifying alpha and replace by distance

    def _collisions_to_detections(self, playground, collision_points):
        """
        Transforms pymunk collisions into simpler data structures.

        Args:
            playground (:obj: :Playground:): playground where the sensor is.
            collision_points: dictionary of collision points

        Returns:
            list of detections

        """

        detections = []

        for sensor_angle, collision in collision_points.items():

            if collision:

                element_colliding = playground.get_entity_from_shape(
                    pm_shape=collision.shape)
                distance = collision.alpha * self._max_range

                detection = Detection(entity=element_colliding,
                                      distance=distance,
                                      angle=sensor_angle)

                detections.append(detection)

        return detections

    def _apply_normalization(self):

        for index, detection in enumerate(self.sensor_values):

            new_detection = Detection(entity=detection.entity,
                                      distance=detection.distance /
                                      self._sensor_max_value,
                                      angle=detection.angle)
            self.sensor_values[index] = new_detection

    def _apply_noise(self):

        raise ValueError('Noise not implemented for Semantic sensors')

    def draw(self, width, *_):

        img = np.zeros((width, width, 3))

        for detection in self.sensor_values:

            distance = detection.distance
            if self._normalize:
                distance *= self._max_range

            distance *= width / (2 * self._max_range)

            pos_x = int(width / 2 - distance * math.cos(-detection.angle))
            pos_y = int(width / 2 - distance * math.sin(-detection.angle))

            rr, cc = line(int(width / 2), int(width / 2), pos_x, pos_y)
            img[rr, cc] = (0.5, 0.1, 0.3)

            rr, cc = disk((pos_x, pos_y), 2)
            img[rr, cc] = [c / 255 for c in detection.entity.base_color[::-1]]

        return img


class SemanticCones(SemanticRay):
    """
    maximum angle of cones should be
    """

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 remove_duplicates=False,
                 **kwargs):
        """
        Args:
            anchor: Entity on which the Lidar is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            remove_occluded: remove occluded detections along cone.
            allow_duplicates: remove duplicates across cones.
                Keep the closest detection for each detected Entity.
            **kwargs: Additional Parameters.

        Keyword Args:
            n_cones: number of cones evenly spaced across the field of view.
            rays_per_cone: number of ray per cone.
            resolution: minimum size of detected objects.
            fov: field of view
            range: range of the rays.
        """
        default_config = parse_configuration('agent_sensors', SensorTypes.SEMANTIC_CONE)
        kwargs = {**default_config, **kwargs}

        self.number_cones = kwargs['n_cones']
        rays_per_cone = kwargs['rays_per_cone']

        if not rays_per_cone > 0:
            raise ValueError('rays_per_cone should be at least 1')

        n_rays = rays_per_cone * self.number_cones

        kwargs['resolution'] = n_rays
        kwargs['n_rays'] = n_rays

        super().__init__(anchor,
                         invisible_elements=invisible_elements,
                         number_rays=n_rays,
                         remove_duplicates=remove_duplicates,
                         **kwargs)

        if self.number_cones == 1:
            self.angles_cone_center = [0]
        else:
            angle = self._fov - self._fov / self.number_cones
            self.angles_cone_center = [
                n * angle / (self.number_cones - 1) - angle / 2
                for n in range(self.number_cones)
            ]

    def _compute_raw_sensor(self, playground, *_):

        super()._compute_raw_sensor(playground)

        detections_per_cone = {}
        for cone_angle in self.angles_cone_center:
            detections_per_cone[cone_angle] = []

        for detection in self.sensor_values:
            # pylint: disable=all
            cone_angle = min(self.angles_cone_center,
                             key=lambda x: (x - detection.angle)**2)
            detections_per_cone[cone_angle].append(detection)

        # detections_per_cone = {k: v for k, v in detections_per_cone.items() if v != []}

        self.sensor_values = []

        for cone_angle, detections in detections_per_cone.items():

            if detections:
                detection = min(detections, key=attrgetter('distance'))

                new_detection = Detection(entity=detection.entity,
                                          distance=detection.distance,
                                          angle=cone_angle)

                self.sensor_values.append(new_detection)

    def draw(self, width, *_):

        img = np.zeros((width, width, 3))

        for detection in self.sensor_values:

            distance = detection.distance
            if self._normalize:
                distance *= self._max_range

            distance *= width / (2 * self._max_range)

            pos_x_1 = int(
                width / 2 - distance *
                math.cos(-detection.angle - self._fov / self.number_cones / 2))
            pos_y_1 = int(
                width / 2 - distance *
                math.sin(-detection.angle - self._fov / self.number_cones / 2))

            pos_x_2 = int(
                width / 2 - distance *
                math.cos(-detection.angle + self._fov / self.number_cones / 2))
            pos_y_2 = int(
                width / 2 - distance *
                math.sin(-detection.angle + self._fov / self.number_cones / 2))

            # pylint: disable=no-member

            rr, cc = line(int(width / 2), int(width / 2), pos_x_1, pos_y_1)
            img[rr, cc] = (0.5, 0.1, 0.3)

            rr, cc = line(pos_x_1, pos_y_1, pos_x_2, pos_y_2)
            img[rr, cc] = (0.5, 0.1, 0.3)

            rr, cc = line(pos_x_2, pos_y_2, int(width / 2), int(width / 2))
            img[rr, cc] = (0.5, 0.1, 0.3)

        return img
