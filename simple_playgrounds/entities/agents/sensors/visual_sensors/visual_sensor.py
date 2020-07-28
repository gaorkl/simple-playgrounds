"""
Base class for VisualSensor.
"""
import os
import math
from abc import abstractmethod

import yaml
import cv2
import numpy as np
import pygame

from simple_playgrounds.entities.agents.sensors.sensor import Sensor
from simple_playgrounds.utils.definitions import SensorModality

#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-function-args
#pylint: disable=no-member


class VisualSensor(Sensor):
    """
    VisualSensor compute their value based on the image of the environment.
    They are first person view sensors, centered and oriented on the anchor.

    """
    sensor_modality = SensorModality.VISUAL

    sensor_type = 'visual'

    def __init__(self, anchor, invisible_elements=None, normalize=False, **kwargs):
        """

        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True.
            **kwargs: Other Keyword Arguments.

        Keyword Args:
            resolution: resolution in pixels.
            range: maximum range of the sensor in pixels.
            fov: opening angle, or field of view, of the sensor.
            min_range: minimal range of the sensor. Below that, everything is set to 0.
        """

        default_config = self.parse_configuration(self.sensor_type)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor, invisible_elements, **kwargs)

        # Field of View of the Sensor
        self._resolution = kwargs.get('resolution')
        self._range = kwargs.get('range')

        self._fov = kwargs.get('fov') * math.pi / 180
        self._min_range = kwargs.get('min_range', 0)

        self.topdow_view = None
        self.polar_view = None

        self.normalize = normalize

        self._center = [0, 0]
        self._scale_ratio = 1.0
        self._pixels_per_degrees = self._resolution / (360 * self._fov / (2 * math.pi))
        self._w_projection_img = int(360 * self._pixels_per_degrees)

        # self.sensor_params = kwargs
        self.sensor_value = None

        # py-lint: disable=too-many-function-args
        self._sensor_surface = pygame.Surface((2*self._range+1, 2*self._range+1),
                                              pygame.SRCALPHA)

    @staticmethod
    def parse_configuration(key):
        """ Parse configurations of different visual sensors. """
        if key is None:
            return {}

        fname = 'visual_sensor_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[key]

    def _crop_image(self, img):

        width, height, _ = img.shape


        # # Position of the sensor
        sensor_x, sensor_y = self.anchor.pm_body.position

        sensor_angle = (self.anchor.pm_body.angle + math.pi/2)%(2*math.pi)

        theta_left = (sensor_angle + self._fov / 2.0)%(2*math.pi)
        theta_right = (sensor_angle - self._fov / 2.0)%(2*math.pi)

        pos_left = ( self._range * math.cos(theta_left), self._range * math.sin(theta_left) )
        pos_right = ( self._range * math.cos(theta_right), self._range * math.sin(theta_right) )

        pts_extrema = [pos_left, pos_right, (0,0)]

        # angle 0
        angles = [0, math.pi/2, 2*math.pi/2, 3*math.pi/2]

        for angle in angles:

            pt = (self._range * math.cos(angle), self._range * math.sin(angle))

            if self._fov == 2*math.pi:
                pts_extrema.append(pt)

            elif angle == 0:

                if theta_right > theta_left:
                    pts_extrema.append(pt)

            else:

                if theta_left >= angle:

                    if theta_right <= angle or theta_left <= theta_right:
                        pts_extrema.append(pt)

                if theta_left < angle:

                    if theta_left <= theta_right <= angle:
                        pts_extrema.append(pt)

        # if theta_left <= theta_right <= 2*math.pi:
        #     theta_right = theta_right - 2*math.pi

        x_min = min([x for x,y in pts_extrema])
        x_max = max([x for x,y in pts_extrema])
        y_min = min([y for x,y in pts_extrema])
        y_max = max([y for x,y in pts_extrema])

        # print(x_min, x_max, y_min, y_max)

        y_1 = int(max(0,  (height - sensor_y) + x_min))
        y_2 = int(min(height, (height - sensor_y) + x_max))

        x_2 = width - int(max(0, sensor_x + y_min))
        x_1 = width - int(min(width, sensor_x + y_max))

        self._center = (((height - sensor_y) - y_1), ((width - sensor_x) - x_1))

        cropped_img = img[x_1:x_2, y_1:y_2]

        return cropped_img

    @abstractmethod
    def update_sensor(self, img):

        cropped_img = self._crop_image(img)
        sensor_angle = (math.pi / 2 - self.anchor.pm_body.angle)

        if cropped_img.shape[0] < self._w_projection_img:

            self._scale_ratio = float(self._w_projection_img) / cropped_img.shape[0]
            self._center = (self._center[0]*self._scale_ratio, self._center[1]*self._scale_ratio)

            new_size = (int(cropped_img.shape[1] * self._scale_ratio),
                        int(cropped_img.shape[0] * self._scale_ratio))
            scaled_img = cv2.resize(cropped_img, new_size, interpolation=cv2.INTER_NEAREST)

        else:
            self._scale_ratio = 1.0
            scaled_img = cropped_img

        polar_img = cv2.linearPolar(scaled_img, self._center,
                                    self._range * self._scale_ratio,
                                    flags=cv2.INTER_NEAREST+cv2.WARP_FILL_OUTLIERS)

        angle_center = scaled_img.shape[0] * (sensor_angle % (2 * math.pi)) / (2 * math.pi)
        rolled_img = np.roll(polar_img, int(scaled_img.shape[0] - angle_center), axis=0)

        start_crop = int(self._min_range * scaled_img.shape[1] / self._range)

        n_pixels = int(scaled_img.shape[0] * (self._fov / 2) / (2 * math.pi))

        cropped_img = rolled_img[int(scaled_img.shape[0] / 2.0 - n_pixels):
                                 int(scaled_img.shape[0] / 2.0 + n_pixels),
                                 start_crop:]

        self.polar_view = cropped_img[:, :, :]

    @property
    @abstractmethod
    def shape(self):
        pass

    @abstractmethod
    def apply_normalization(self):
        pass
