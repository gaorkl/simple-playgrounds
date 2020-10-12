"""
Module for Vision Sensors.
"""
import numpy as np
import cv2
import math
from skimage.draw import line

from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

#pylint: disable=line-too-long
#pylint: disable=too-many-locals
#pylint: disable=no-member


class RgbSensor(VisualSensor):

    """
    Provides a 1D image from the point of view of the anchor.
    Similar to RGB camera, as a single line of pixels.
    """
    sensor_type = 'rgb'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):

        super().__init__(anchor, invisible_elements, normalize=normalize, **kwargs)

        if self._resolution == 1:
            self.angles = [0]
        else:
            self.angles = [n * self._fov / (self._resolution - 1) - self._fov / 2 for n in range(self._resolution)]

        self.sensor_value = np.zeros(self.shape)

        self._center = (self.range, self.range)

        self.cropped_img = np.zeros((2 * self.range + 1, 2 * self.range + 1, 3))

        self.n_precomputed_angles = 5000
        self.lines = np.ones((self.n_precomputed_angles, 2, 2*self.range), dtype=int) * self._center[0]

        for n in range(self.n_precomputed_angles):
            angle = 2*math.pi*n/self.n_precomputed_angles

            rr, cc = self._compute_pixels(angle)

            self.lines[n, 0, :len(rr)] = rr[:]
            self.lines[n, 1, :len(rr)] = cc[:]

        self.indices = np.arange(self._resolution)

    def _compute_pixels(self, sensor_angle):

        angle = sensor_angle - math.pi / 2

        position_end = (self._center[0] + (self.range - 1) * math.cos(-angle),
                        self._center[1] + (self.range - 1) * math.sin(-angle)
                        )

        rr, cc = line( int(self._center[0]), int(self._center[1]), int(position_end[0]), int(position_end[1]) )

        rr = np.clip(rr, 0, self.cropped_img.shape[0])
        cc = np.clip(cc, 0, self.cropped_img.shape[1])

        rr_filtered = [r for r, c in zip(rr, cc) if 0 <= r < self.cropped_img.shape[0]
                       and 0 <= c < self.cropped_img.shape[1] ]
        cc_filtered = [ c for r, c in zip(rr, cc) if 0 <= r < self.cropped_img.shape[0]
                        and 0 <= c < self.cropped_img.shape[1] ]

        return rr_filtered, cc_filtered

    def compute_raw_sensor(self, img):

        angles = [ (self.anchor.pm_body.angle + sensor_angle)%(2*math.pi) for sensor_angle in self.angles ]
        number_angles = [int( angle * self.n_precomputed_angles/(2*math.pi)) for angle in angles ]

        lines_coord = self.lines[number_angles]
        pixels = img[lines_coord[:,0], lines_coord[:,1]]

        self.sensor_value = pixels[self.indices, np.argmax(pixels.any(axis=2), axis = 1)].astype(float)

        self.sensor_value = self.sensor_value[:,::-1].astype(float)

    @property
    def shape(self):
        return self._resolution, 3

    def draw(self, width_display, height_sensor):

        im = np.expand_dims(self.sensor_value, 0)
        im = cv2.resize(im, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)
        if self.normalize is False: im /= 255.

        return im


class GreySensor(RgbSensor):
    """
    Provides a 1D image from the point of view of the anchor.
    Similar to Grey-level camera, as a single line of pixels.
    """
    sensor_type = 'grey'

    def update_sensor(self, img):
        super().update_sensor(img)

        self.sensor_value = np.dot(self.sensor_value[..., :3], [0.114, 0.299, 0.587])

    @property
    def shape(self):
        return self._resolution

    def draw(self, width_display, height_sensor):

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        im = np.expand_dims(expanded, 0)
        im = cv2.resize(im, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False: im /= 255.

        return im
