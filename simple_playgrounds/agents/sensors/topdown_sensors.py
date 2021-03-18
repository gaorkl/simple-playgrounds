"""
Module that defines TopDown Sensors.
Topdown sensors are based computed using the image provided by the environment.
"""
import math
import numpy as np

from skimage.transform import resize, rotate
from skimage import draw
import pygame

from simple_playgrounds.agents.sensors.sensor import Sensor
from simple_playgrounds.utils.definitions import SensorTypes
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=no-member


class TopdownSensor(Sensor):
    """
    TopdownSensor provides an image from bird's eye view, centered and oriented on the anchor.
    The anchor is, by default, visible to the agent.
    """
    sensor_type = SensorTypes.TOP_DOWN
    sensor_modality = SensorTypes.VISUAL

    def __init__(self, anchor, invisible_elements=None,
                 normalize=True, noise_params=None, only_front=False,
                 **sensor_params):
        """
        Refer to Sensor Class.

        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True
            only_front: Only return the half part of the Playground that the Sensor faces.
                Remove what is behind the sensor. Default: False.
        """

        default_config = parse_configuration('agent_sensors', self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor=anchor, invisible_elements=invisible_elements, normalize=normalize,
                         noise_params=noise_params, **sensor_params)

        self._invisible_elements.remove(anchor)

        self.only_front = only_front

        self._center = (int(self._resolution / 2) - 1, int(self._resolution / 2) - 1)

        # Calculate range with circle

        mask_circle = np.zeros((self._resolution, self._resolution), dtype=bool)
        rr, cc = draw.disk((self._center[0], self._center[1]), (int(self._resolution / 2) - 1), shape=mask_circle.shape)
        mask_circle[rr, cc] = 1

        # Calculate fov with poly

        points = [[(int(self._resolution / 2) - 1), 0],
                  [0, 0],
                  [0, self._resolution],
                  [(int(self._resolution / 2) - 1), self._resolution]]

        if self._fov > math.pi:
            points = [[self._resolution, 0]] + points + [[self._resolution, self._resolution]]

        r1 = self._center[0] - (int(self._resolution/2) - 1) * np.sin(math.pi/2 + self._fov/2)
        c1 = self._center[1] + (int(self._resolution/2) - 1) * np.cos(math.pi/2 + self._fov/2)

        r2 = self._center[0] - (int(self._resolution/2) - 1) * np.sin(math.pi/2 - self._fov/2)
        c2 = self._center[1] + (int(self._resolution/2) - 1) * np.cos(math.pi/2 - self._fov/2)

        points = points + [[r2, c2], self._center, [r1, c1]]
        mask_poly = draw.polygon2mask((self._resolution, self._resolution), np.array(points))

        self.mask_total_fov = mask_circle & mask_poly

        self._sensor_max_value = 255

    def get_local_sensor_image(self, playground, sensor_surface):

        all_agent_parts = []
        for agent in playground.agents:
            all_agent_parts += agent.parts

        # take all elems and body parts which are close to sensor
        sc_elems = [elem for elem in playground.scene_elements if
                    self._check_elem(elem)]
        sc_elems += [elem for elem in all_agent_parts if
                     self._check_elem(elem)]

        # filter invisible
        visible_sc_elems = [elem for elem in sc_elems if elem not in self._invisible_elements]

        # Draw elements that are not invisible to this agent
        for element in visible_sc_elems:
            element.draw(sensor_surface)

        cropped = pygame.Surface((2 * self._range + 1, 2 * self._range + 1))

        pos_x = self.anchor.position[0] + self._range - playground.width
        pos_y = - self.anchor.position[1] + self._range
        cropped.blit(sensor_surface, (pos_x, pos_y))

        img_cropped = pygame.surfarray.pixels3d(cropped).astype(float)

        return img_cropped

    def _check_elem(self, elem):

        vis_shape = elem.pm_visible_shape

        if vis_shape is not None:
            contact_points = vis_shape.shapes_collide(self.anchor.pm_visible_shape).points
            return (not elem.background) and len(contact_points) == 0

        return not elem.background

    def _compute_raw_sensor(self, playground, sensor_surface):

        cropped_img = self.get_local_sensor_image(playground, sensor_surface)

        small_img = resize(cropped_img, (self._resolution, self._resolution),
                           order=0, preserve_range=True)

        rotated_img = rotate(small_img, self.anchor.pm_body.angle * 180 / math.pi + 90)

        masked_img = rotated_img
        masked_img[self.mask_total_fov == 0] = 0

        if self.only_front:
            masked_img = masked_img[:int(self._resolution / 2), ...]

        self.sensor_values = masked_img[:, ::-1, ::-1]

    def _apply_normalization(self):
        self.sensor_values /= self._sensor_max_value

    def _apply_noise(self):

        if self._noise_type == 'gaussian':

            additive_noise = np.random.normal(self._noise_mean, self._noise_scale, size=self.shape)

        elif self._noise_type == 'salt_pepper':

            proba = [self._noise_probability/2,
                     1-self._noise_probability,
                     self._noise_probability/2]
            additive_noise = np.random.choice([-self._sensor_max_value, 0, self._sensor_max_value],
                                              p=proba,
                                              size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values > self._sensor_max_value] = self._sensor_max_value

    @property
    def shape(self):

        if self.only_front:
            return int(self._resolution / 2), self._resolution, 3
        return self._resolution, self._resolution, 3

    def draw(self, width, *_):

        height_display = int(width * self.shape[0] / self.shape[1])

        image = resize(self.sensor_values, (height_display, width), order=0, preserve_range=True)

        if not self._apply_normalization:
            image /= 255.

        return image


class FullPlaygroundSensor(Sensor):
    """
    FullPlaygroundSensor provides an image from bird's eye view of the full playground.
    There is no anchor.
    """
    sensor_type = SensorTypes.FULL_PLAYGROUND
    sensor_modality = SensorTypes.VISUAL

    def __init__(self, size_playground, invisible_elements=None, normalize=True, noise_params=None,
                 **sensor_params):
        """
        Refer to Sensor Class.

        Args:
            size_playground: Needed to calculate the shape of the sensor values.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True
            only_front: Only return the half part of the Playground that the Sensor faces.
                Remove what is behind the sensor. Default: False.
        """

        default_config = parse_configuration('agent_sensors', self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor=None, invisible_elements=invisible_elements, normalize=normalize,
                         noise_params=noise_params, **sensor_params)

        max_size_playground = max(size_playground)
        self._scale = (int(self._resolution * size_playground[1] / max_size_playground),
                       int(self._resolution * size_playground[0] / max_size_playground))

        self._sensor_max_value = 255

    def get_sensor_image(self, playground, sensor_surface):

        all_agent_parts = []
        for agent in playground.agents:
            all_agent_parts += agent.parts

        # take all elems and body parts which are close to sensor
        sc_elems = playground.scene_elements + all_agent_parts

        # filter invisible
        visible_sc_elems = [elem for elem in sc_elems if elem not in self._invisible_elements]

        # Draw elements that are not invisible to this agent
        for element in visible_sc_elems:
            element.draw(sensor_surface)

        img = pygame.surfarray.pixels3d(sensor_surface).astype(float)
        np_image = np.rot90(img, 1, (1, 0))
        np_image = np_image[::-1, :, ::-1]

        return np_image

    def _compute_raw_sensor(self, playground, sensor_surface):

        full_image = self.get_sensor_image(playground, sensor_surface)

        self.sensor_values = resize(full_image, (self._scale[0], self._scale[1]), order=0, preserve_range=True)

    def _apply_normalization(self):
        self.sensor_values /= self._sensor_max_value

    def _apply_noise(self):

        if self._noise_type == 'gaussian':

            additive_noise = np.random.normal(self._noise_mean, self._noise_scale, size=self.shape)

        elif self._noise_type == 'salt_pepper':

            additive_noise = np.random.choice([-self._sensor_max_value, 0, self._sensor_max_value],
                                              p=[self._noise_probability / 2, 1 - self._noise_probability,
                                                 self._noise_probability / 2],
                                              size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values > self._sensor_max_value] = self._sensor_max_value

    @property
    def shape(self):

        return self._scale[0], self._scale[1], 3

    def draw(self, width, *_):

        height_display = int(width * self.shape[0] / self.shape[1])

        image = resize(self.sensor_values, (width, height_display), order=0, preserve_range=True)

        if not self._apply_normalization:
            image /= 255.

        return image
