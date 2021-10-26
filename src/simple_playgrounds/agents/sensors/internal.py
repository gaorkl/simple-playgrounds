""" Module implementing robotic sensors: Cameras, Lidar, touch sensing.

These sensors are very close to physical sensors that could be used on real robots.
These sensors can be noisy.
Importantly, as Simple-Playgrounds is a 2D environments, these sensors are 1D.
"""
import math

from abc import ABC

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .sensor import SensorDevice


class InternalSensor(SensorDevice, ABC):

    """
    Base Class for Internal Sensors.
    """

    def __init__(self,
                 anchor,
                 noise_params=None,
                 normalize=False,
                 **_,
                 ):
        """
        Internal Sensors calculate numerical values such as position or speed.

        Args:
            anchor: Body Part or Scene Element on which the sensor will be attached.
            noise_params: Dictionary of noise parameters.
                Noise is applied to the raw sensor, before normalization.
            normalize: boolean. If True, sensor values are scaled between 0 and 1.

        Noise Parameters:
            type: 'gaussian'
            mean: mean of gaussian noise (default 0)
            scale: scale (or std) of gaussian noise (default 1)

        """

        super().__init__(anchor=anchor,
                         noise_params=noise_params,
                         fov=1,
                         resolution=1,
                         max_range=1,
                         normalize=normalize,
                         )

    def _get_null_sensor(self):
        return np.zeros(self.shape)

    def _apply_noise(self):
        if self._noise_type == 'gaussian':
            additive_noise = np.random.normal(self._noise_mean,
                                              self._noise_scale,
                                              size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

    def draw(self, width: int, height: int):
        img = Image.new("RGB", (width, height), (255, 255, 255))
        drawer_image = ImageDraw.Draw(img)

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", int(height * 1 / 2))
        values_str = ", ".join(["%.2f" % e for e in self.sensor_values])
        w_text, h_text = fnt.getsize(text=values_str)
        pos_text = ((width - w_text) / 2, (height - h_text) / 2)
        drawer_image.text(pos_text,
                          values_str,
                          font=fnt,
                          fill=(0, 0, 0))

        return np.asarray(img) / 255


class Position(InternalSensor):

    """
    Position Sensor returns a numpy array containing the position x, y and the
    orientation of the anchor.
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.requires_playground_size = True

    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.position),
                                             [self._anchor.angle]])

    def set_playground_size(self, size):
        self._pg_size = size

    def _apply_normalization(self):
        self.sensor_values /= (self._pg_size[0], self._pg_size[1], 2*math.pi)

    @property
    def shape(self):
        return (3,)


class Velocity(InternalSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.velocity),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (3,)


class Time(InternalSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.array(playground.steps)

    def _apply_normalization(self):
        pass

    @property
    def shape(self):
        return (1,)
