"""
Base class for VisualSensor.
"""
import os
import math
from abc import abstractmethod

import yaml

from simple_playgrounds.entities.agents.sensors.sensor import Sensor
from simple_playgrounds.utils.definitions import SensorModality

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-function-args
# pylint: disable=no-member


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
        self.range = kwargs.get('range')

        self._fov = kwargs.get('fov') * math.pi / 180

        self.normalize = normalize
        self.noise = kwargs.get('noise', None)

        self._center = (self.range, self.range)

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

    def apply_noise(self):
        pass

    def apply_normalization(self):
        self.sensor_value /= 255.

    def compute_raw_sensor(self, img):
        pass

    def update_sensor(self, img):

        self.compute_raw_sensor(img)

        if self.noise is not None:
            self.apply_noise()

        if self.normalize:
            self.apply_normalization()

    @property
    @abstractmethod
    def shape(self):
        pass
