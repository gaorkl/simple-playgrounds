from ..sensor import Sensor
from flatland.utils.definitions import SensorModality

from abc import abstractmethod

import pygame
import math
import cv2
import numpy as np

import os
import yaml


class VisualSensor(Sensor):

    sensor_modality = SensorModality.VISUAL

    sensor_type = 'visual'

    def __init__(self, anchor, invisible_elements, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        # Field of View of the Sensor
        self.fovResolution = sensor_params.get('resolution')
        self.fovRange = sensor_params.get('range')

        self.fovAngle = sensor_params.get('fov') * math.pi / 180
        self.min_range = sensor_params.get('min_range', 0)

        self.topdow_view = None
        self.polar_view = None
        self.center = [0, 0]
        self.scale_ratio = 1.0

        self.pixels_per_degrees = self.fovResolution / (360 * self.fovAngle / (2*math.pi))

        self.w_projection_img = int(360*self.pixels_per_degrees)

        self.sensor_params = sensor_params

        self.sensor_surface = pygame.Surface((2*self.fovRange + 1, 2*self.fovRange + 1), pygame.SRCALPHA)

    @staticmethod
    def parse_configuration(key):
        if key is None:
            return {}

        fname = 'visual_sensor_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]

    @abstractmethod
    def update_sensor(self, img, entities, agents):

        w, h, _ = img.shape

        # # Position of the sensor
        sensor_x, sensor_y = self.anchor_body.position
        sensor_angle = (math.pi / 2 - self.anchor_body.angle)

        x1 = int(max(0, (w - sensor_x) - self.fovRange))
        x2 = int(min(w, (w - sensor_x) + self.fovRange))

        y1 = int(max(0, (h - sensor_y) - self.fovRange))
        y2 = int(min(h, (h - sensor_y) + self.fovRange))

        center = (((h - sensor_y) - y1),  ((w - sensor_x) - x1))
        self.center = center
        cropped_img = img[x1:x2, y1:y2]

        if cropped_img.shape[0] < self.w_projection_img:

            self.scale_ratio = float(self.w_projection_img) / cropped_img.shape[0]
            center = (center[0] * self.scale_ratio, center[1] * self.scale_ratio)

            new_size = (int(cropped_img.shape[1]*self.scale_ratio), int(cropped_img.shape[0]*self.scale_ratio))
            scaled_img = cv2.resize(cropped_img, new_size, interpolation=cv2.INTER_NEAREST)

        else:
            self.scale_ratio = 1.0
            scaled_img = cropped_img

        polar_img = cv2.linearPolar(scaled_img, center,
                                    self.fovRange*self.scale_ratio,
                                    flags=cv2.INTER_NEAREST+cv2.WARP_FILL_OUTLIERS)

        angle_center = scaled_img.shape[0] * (sensor_angle % (2 * math.pi)) / (2 * math.pi)
        rolled_img = np.roll(polar_img, int(scaled_img.shape[0] - angle_center), axis=0)

        start_crop = int(self.min_range * scaled_img.shape[1] / self.fovRange)

        n_pixels = int(scaled_img.shape[0] * (self.fovAngle / 2) / (2 * math.pi))

        cropped_img = rolled_img[
                      int(scaled_img.shape[0] / 2.0 - n_pixels):
                      int(scaled_img.shape[0] / 2.0 + n_pixels),
                      start_crop:
                      ]

        self.polar_view = cropped_img[:, :, :]

    @abstractmethod
    def shape(self):
        pass
