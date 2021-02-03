"""
This Module provides semantic sensors. These artificial sensors return semantic information about the detected entities.
They return the actual instance of the entity detected, which allow to access their attributes.
E.g. position, velocity, mass, shape can be accessed.
"""

import math
import numpy as np
import cv2

from operator import attrgetter

from .sensor import RayCollisionSensor
from simple_playgrounds.utils.definitions import Detection, SensorModality


class SemanticRay(RayCollisionSensor):

    sensor_type = 'semantic-ray'
    sensor_modality = SensorModality.SEMANTIC

    def __init__(self, anchor, invisible_elements=None, normalize=True, noise_params=None,
                 remove_duplicates=True, remove_occluded=True, **sensor_params):

        super().__init__(anchor=anchor, invisible_elements=invisible_elements, normalize=normalize,
                         noise_params=noise_params, remove_duplicates=remove_duplicates, remove_occluded=remove_occluded, **sensor_params)

        self._sensor_max_value = self._range

    def _compute_raw_sensor(self, playground):

        collision_points = self._compute_points(playground)

        collision_points = {k: v for k, v in collision_points.items() if v != []}

        self.sensor_values = self._collisions_to_detections(playground, collision_points)
        # class Point just for modifying alpha and replace by distance

    def _collisions_to_detections(self, playground, collision_points):

            """
            Transforms pymunk collisions into simpler data structures.

            Args:
                collisions: list of collision points

            Returns:
                list of detections

            """

            detections = []

            for sensor_angle, collisions in collision_points.items():

                for collision in collisions:

                    element_colliding = playground.get_entity_from_shape(pm_shape=collision.shape)
                    distance = collision.alpha * self._range

                    detection = Detection(entity=element_colliding, distance=distance, angle=sensor_angle)

                    detections.append(detection)

            return detections

    def _apply_normalization(self):

        for detection in self.sensor_values:
            detection.distance /= self._sensor_max_value

    def _apply_noise(self):

        raise ValueError('Noise not implemented for Semantic sensors')

    def draw(self, size_display, *args, **kwargs):

        img = np.zeros((size_display, size_display, 3))

        for detection in self.sensor_values:

            distance = detection.distance
            if self._normalize:
                distance *= self._range

            distance *= size_display / (2 * self._range)

            pos_x = int(size_display / 2 - distance * math.cos(detection.angle))
            pos_y = int(size_display / 2 - distance * math.sin(detection.angle))

            # pylint: disable=no-member
            cv2.line(img, (int(size_display / 2), int(size_display / 2)), (pos_y, pos_x), color=(0.5, 0.1, 0.3))
            cv2.circle(img, (pos_y, pos_x), 2, [25, 130, 255], thickness=-1)

        return img


class SemanticCones(SemanticRay):
    """
    maximum angle of cones should be
    """

    sensor_type = 'semantic-cone'

    def __init__(self, anchor, invisible_elements=None,
                 remove_occluded=True, remove_duplicates=False, **sensor_params):
        """
        Args:
            anchor: Entity on which the Lidar is attached.
            invisible_elements: Elements which are invisible to the Sensor.
            remove_occluded: remove occluded detections along cone.
            allow_duplicates: remove duplicates across cones.
                Keep the closest detection for each detected Entity.
            **sensor_params: Additional Parameters.

        Keyword Args:
            number_cones: number of cones evenly spaced across the field of view.
            resolution: minimum size of detected objects.
            fov: field of view
            range: range of the rays.
        """
        default_config = self._parse_configuration()
        sensor_params = {**default_config, **sensor_params}

        self.number_cones = sensor_params['n_cones']
        rays_per_cone = sensor_params.get('rays_per_cone')

        assert rays_per_cone > 0

        n_rays = rays_per_cone*self.number_cones

        sensor_params['resolution'] = n_rays
        sensor_params['n_rays'] = n_rays

        super().__init__(anchor, invisible_elements=invisible_elements, number_rays=n_rays,
                         remove_occluded=remove_occluded, remove_duplicates=remove_duplicates, ** sensor_params)

        if self.number_cones == 1:
            self.angles_cone_center = [0]
        else:
            angle = self._fov - self._fov / self.number_cones
            self.angles_cone_center = [n * angle / (self.number_cones - 1) - angle / 2 for n in
                                       range(self.number_cones)]

    def _compute_raw_sensor(self, playground):

        super()._compute_raw_sensor(playground)

        detections_per_cone = {}
        for cone_angle in self.angles_cone_center:
            detections_per_cone[cone_angle] = []

        for detection in self.sensor_values:
            cone_angle = min(self.angles_cone_center, key=lambda x: (x - detection.angle) ** 2)
            detections_per_cone[cone_angle].append(detection)

        # filter for occlusion and duplicates
        if self._remove_occluded:
            for cone_angle, detections in detections_per_cone.items():
                detections = self._remove_cone_occlusions(detections)
                detections_per_cone[cone_angle] = detections

        detections_per_cone = {k: v for k, v in detections_per_cone.items() if v != []}

        self.sensor_values = []

        for cone_angle, detections in detections_per_cone.items():

            for detection in detections:
                detection.angle = cone_angle
                self.sensor_values.append(detection)

    @staticmethod
    def _remove_cone_occlusions(detections):

        if not detections:
            return detections

        min_distance_detection = min(detections, key=attrgetter('distance'))
        return [min_distance_detection]

    def draw(self, size_display, *args, **kwargs):

        img = np.zeros((size_display, size_display, 3))

        for detection in self.sensor_values:

            distance = detection.distance
            if self._normalize:
                distance *= self._range

            distance *= size_display / (2 * self._range)

            pos_x_1 = int(size_display / 2 - distance * math.cos(detection.angle - self._fov / self.number_cones / 2))
            pos_y_1 = int(size_display / 2 - distance * math.sin(detection.angle - self._fov / self.number_cones / 2))

            pos_x_2 = int(size_display / 2 - distance * math.cos(detection.angle + self._fov / self.number_cones / 2))
            pos_y_2 = int(size_display / 2 - distance * math.sin(detection.angle + self._fov / self.number_cones / 2))

            # pylint: disable=no-member
            cv2.line(img, (int(size_display / 2), int(size_display / 2)), (pos_y_1, pos_x_1), color=(0.5, 0.1, 0.3))
            cv2.line(img, (pos_y_1, pos_x_1), (pos_y_2, pos_x_2), color=(0.5, 0.1, 0.3))
            cv2.line(img, (pos_y_2, pos_x_2), (int(size_display / 2), int(size_display / 2)), color=(0.5, 0.1, 0.3))
            # cv2.circle(img, (pos_y, pos_x), 2, [25, 130, 255], thickness=-1)

        return img
