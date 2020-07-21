"""
Module defining the Base Class for Sensors
"""
from abc import abstractmethod, ABC
import numpy
from simple_playgrounds.utils.definitions import SensorModality
from simple_playgrounds.entities.entity import Entity

class Sensor(ABC):
    """
    Base class Sensor.

    Attributes:
        anchor: body Part to which the sensor is attached.
            Sensor is attached to the center of the Part.
        sensor_value: values of the sensor.
        invisible_elements: elements that the sensor does not perceive. List of Parts of SceneElements.
        name: Name of the sensor.

    Note:
        The anchor is always invisible to the sensor.

    """

    index_sensor = 0
    sensor_type = 'sensor'

    def __init__(self, anchor, invisible_elements=None, **sensor_param):

        # Sensor name
        # Internal counter to assign number and name to each sensor
        self.name = sensor_param.get('name', self.sensor_type + '_' + str(Sensor.index_sensor))
        Sensor.index_sensor += 1

        # Anchor of the sensor
        self.anchor = anchor

        # self.sensor_params = sensor_param
        self.sensor_value = None

        if invisible_elements == None:
            invisible_elements = []
        elif isinstance(invisible_elements, Entity ):
            invisible_elements = [invisible_elements]

        self.invisible_elements = [anchor] + invisible_elements

        self._value_range = 255

    @abstractmethod
    def update_sensor(self):
        """ Updates the sensor"""

    @property
    def shape(self):
        """ Returns the shape of the numpy array, if applicable."""
        return None

    def draw(self, width_display, height_sensor):
        """
        Function that creates an image for visualizing a sensor.

        Args:
            width_display: width of the display for drawing.
            height_sensor: when applicable (1D sensor), the height of the display.

        Returns:
            Numpy array containing the visualization of the sensor values.

        """
        return None

# pylint: disable=all


class NoisySensor(Sensor):
    """
    Only for visual sensor.
    Noise on the original sensor (before normalization).
    """
    def __init__(self, sensor, noise_type, dynamic = True, **noise_params):

        assert(sensor.sensor_modality is SensorModality.VISUAL)

        self.__class__ = type(sensor.__class__.__name__,
                              (self.__class__, sensor.__class__),
                              {})
        self.__dict__ = sensor.__dict__

        self.original_update_sensor = sensor.update_sensor

        self.noise_type = noise_type
        self.dynamic = noise_params.get('dynamic', False)

        self.dynamic = dynamic
        self.noise_params = noise_params
        self.noise_application_type = None

        self.compute_noise()

    def compute_noise(self):

        if self.noise_type == 'gaussian':

            mean = self.noise_params.get('mean')
            std = self.noise_params.get('std')

            noise = numpy.random.normal(mean, std, self.shape)
            self.noise_application_type = 'additive'

        elif self.noise_type == 'deadpixel':

            proba = 1 - self.noise_params.get('proba')
            self.noise_application_type = 'multiplicative'

            if isinstance(self.shape, int):
                noise = numpy.random.binomial(1, proba, self.shape).reshape((self.shape, 1))

            elif len(self.shape) == 2:
                noise = numpy.random.binomial(1, proba, self.shape[0]).reshape((self.shape[0], 1))

            else:
                noise = numpy.random.binomial(1, proba, (self.shape[0], self.shape[1], 1))

            self.noise_application_type = 'multiplicative'

        else:
            raise ValueError( 'Noise '+str(self.noise_type)+' not implemented')

        self.noise = noise

    def update_sensor(self, *args, **kwargs):

        norm = self.normalize

        self.normalize = False
        self.original_update_sensor(*args, **kwargs)

        if self.dynamic:
            self.compute_noise()

        if self.noise_application_type == 'multiplicative':
            self.sensor_value = numpy.multiply(self.sensor_value, self.noise)

        else:
            self.sensor_value = numpy.add(self.sensor_value, self.noise)

        self.sensor_value.clip(0, self._value_range)

        self.normalize = norm

        self.apply_normalization()
