"""
Module defining the Base Classes for Sensors.
"""

from abc import abstractmethod, ABC
import os
import yaml
import math
import pymunk
import numpy as np

from operator import attrgetter

from simple_playgrounds.utils.definitions import SensorModality
from simple_playgrounds.entity import Entity


class Sensor(ABC):
    """ Base class Sensor, used as an Interface for all sensors.

    Attributes:
        anchor: body Part to which the sensor is attached.
            Sensor is attached to the center of the Anchor.
        sensor_values: current values of the sensor.
        name: Name of the sensor.

    Class Attributes:
        sensor_type: string that represents the type of sensor (e.g. 'rgb' or 'lidar').

    Note:
        The anchor is always invisible to the sensor.

    """

    _index_sensor = 0
    sensor_type = 'sensor'

    def __init__(self, anchor, fov, resolution, max_range,
                 invisible_elements, normalize, noise_params, name=None, **kwargs):
        """
        Sensors are attached to an anchor. They detect every visible Entity (Parts or Scene Elements).
        If the entity is in invisible elements, it is not detected.

        Args:
            anchor: Body Part or Scene Element on which the sensor will be attached.
            fov: Field of view of the sensor (in degrees).
            resolution: Resolution of the sensor (in pixels, or number of rays).
            max_range: maximum range of the sensor (in the same units as the playground distances).
            invisible_elements: list of elements invisible to the sensor.
            normalize: boolean. If True, sensor values are scaled between 0 and 1.
            noise_params: Dictionary of noise parameters. Noise is applied to the raw sensor, before normalization.
            name: name of the sensor. If not provided, a name will be chosen by default.

        Noise Parameters:
            type: 'gaussian', 'salt_pepper'
            mean: mean of gaussian noise (default 0)
            scale: scale / std of gaussian noise (default 1)
            salt_pepper_probability: probability for a pixel to be turned off or max

        """

        # Sensor name
        # Internal counter to assign number and name to each sensor
        if name is not None:
            self.name = name
        else:
            self.name = self.sensor_type + '_' + str(Sensor._index_sensor)
            Sensor._index_sensor += 1

        self.anchor = anchor
        self.sensor_values = None

        if invisible_elements is None:
            invisible_elements = []
        elif isinstance(invisible_elements, Entity):
            invisible_elements = [invisible_elements]
        self._invisible_elements = [anchor] + invisible_elements

        self._normalize = normalize

        self._noise = False
        if noise_params is not None:
            self._noise = True
            self._noise_type = noise_params.get('type', 'gaussian')

            if self._noise_type == 'gaussian':
                self._noise_mean = noise_params.get('mean', 0)
                self._noise_scale = noise_params.get('scale', 1)

            elif self._noise_type == 'salt_pepper':
                self._noise_probability = noise_params.get('probability', 0.1)

            else:
                raise ValueError('Noise type not implemented')

        self._range = max_range
        self._fov = fov * math.pi / 180
        self._resolution = resolution

        assert self._range > 0
        assert self._fov > 0
        assert self._resolution > 0

        # Sensor max value is used for noise and normalization calculation
        self._sensor_max_value = None

    def update(self, **kwargs):
        """
        Updates the attribute sensor_values.
        Applies normalization and noise if necessary.

        Args:
            **kwargs: either playground, or playground

        Returns:

        """
        self._compute_raw_sensor(**kwargs)

        if self._noise:
            self._apply_noise()

        if self._normalize:
            self._apply_normalization()

    def _parse_configuration(self):

        file_name = '../../utils/configs/agent_sensors.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, file_name), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[self.sensor_type]

    @abstractmethod
    def _compute_raw_sensor(self, **kwargs):
        pass

    @abstractmethod
    def _apply_normalization(self):
        pass

    @abstractmethod
    def _apply_noise(self):
        pass

    @property
    def shape(self):
        """ Returns the shape of the numpy array, if applicable."""
        return None

    @abstractmethod
    def draw(self, **kwargs):
        """
        Function that creates an image for visualizing a sensor.

        Keyword Args:
            width: width of the returned image
            height: when applicable (in the case of 1D sensors), the height of the image.

        Returns:
            Numpy array containing the visualization of the sensor values.

        """
        return None


class RayCollisionSensor(Sensor, ABC):

    sensor_modality = SensorModality.ROBOTIC

    """
    Base class for Ray Collision sensors.
    Ray collisions are computed using pymunk segment queries, that detect intersection with obstacles.
    Robotic sensors and Semantic sensors inherit from this class.

    """

    def __init__(self, remove_occluded, remove_duplicates, **sensor_params):

        default_config = self._parse_configuration()
        sensor_params = {**default_config, **sensor_params}

        super().__init__(**sensor_params)

        self._remove_occluded = remove_occluded
        self._remove_duplicates = remove_duplicates

        # Need to remove occluded before removing duplicates
        if remove_duplicates:
            self._remove_occluded = True

        # Field of View of the Sensor
        if self._resolution == 1:
            self._ray_angles = [0]
        else:
            self._ray_angles = [n * self._fov / (self._resolution - 1) - self._fov / 2 for n in range(self._resolution)]

        #self._filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS() )#^ 0b1)

        self._invisible_shapes = []

        for entity in self._invisible_elements:
            self._invisible_shapes += [entity.pm_visible_shape, entity.pm_interaction_shape]
        self._invisible_shapes = list(set(self._invisible_shapes))
        if None in self._invisible_shapes:
            self._invisible_shapes.remove(None)

    @staticmethod
    def _remove_occlusions(collisions):

        if not collisions:
            return collisions

        min_distance_point = min(collisions, key=attrgetter('alpha'))
        return [min_distance_point]

    @staticmethod
    def _remove_duplicate_collisions(collisions_by_angle):

        all_shapes = list(set(col[0].shape for angle, col in collisions_by_angle.items() if col != []))

        all_collisions = []
        for angle, cols in collisions_by_angle.items():
            all_collisions += cols

        all_min_collisions = []
        for shape in all_shapes:
            min_col = min([col for col in all_collisions if col.shape is shape],
                          key=attrgetter('alpha'))
            all_min_collisions.append(min_col)

        # Filter out noon-min collisions
        for angle, col in collisions_by_angle.items():
            if col != [] and col[0] not in all_min_collisions:
                collisions_by_angle[angle] = []

        return collisions_by_angle

    def _compute_collisions(self, playground, sensor_angle):

        position = self.anchor.pm_body.position
        angle = self.anchor.pm_body.angle + sensor_angle

        position_end = (position[0] + self._range * math.cos(angle),
                        position[1] + self._range * math.sin(angle)
                        )

        collisions = playground.space.segment_query(position, position_end, 1, pymunk.ShapeFilter())


        # remove invisible entities
        collisions = [col for col in collisions
                      if col.shape not in self._invisible_shapes and col.shape.sensor is not True]

        # filter occlusions
        if self._remove_occluded:
            collisions = self._remove_occlusions(collisions)

        return collisions

    def _compute_points(self, pg):

        points = {}

        for sensor_angle in self._ray_angles:

            collisions = self._compute_collisions(pg, sensor_angle)
            points[sensor_angle] = collisions

        if self._remove_duplicates:
            points = self._remove_duplicate_collisions(points)

        return points

    def _apply_noise(self):

        if self._noise_type == 'gaussian':

            additive_noise = np.random.normal(self._noise_mean, self._noise_scale, size = self.shape)

        elif self._noise_type == 'salt_pepper':

            additive_noise = np.random.choice([-self._sensor_max_value, 0, self._sensor_max_value],
                                               p=[self._noise_probability/2, 1-self._noise_probability, self._noise_probability/2],
                                               size= self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values > self._sensor_max_value] = self._sensor_max_value