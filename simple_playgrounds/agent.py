""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard commands.

Examples can be found in simple_playgrounds/agents/agents.py
"""
from abc import ABC

import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from simple_playgrounds.utils.definitions import ActionSpaces
from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.agents.parts.actuators import Grasp

# pylint: disable=too-many-instance-attributes
# pylint: disable=no-member

_BORDER_IMAGE = 3


class Agent(ABC):
    """
    Base class for agents

    """
    index_agent = 0
    in_a_playground = False

    def __init__(self, base_platform, name=None, noise_params=None):
        """
        Base class for agents.

        Args:
            base_platform: Platform object, required to initialize an agent.
                All agents have a Platform.
            name: Name of the agent. If not provide, a name will be added by default.
            noise_params: Dictionary of noise parameters.
                Noise is applied to the actuator, before action.

        Noise Parameters:
            type: 'gaussian'
            mean: mean of gaussian noise (default 0)
            scale: scale / std of gaussian noise (default 1)
        """

        if name is None:
            self.name = 'agent_' + str(Agent.index_agent)
        else:
            self.name = name
        Agent.index_agent += 1

        # List of sensors
        self.sensors = []

        # Body parts
        self.base_platform = base_platform
        self.parts = [self.base_platform]

        # Default starting position
        self.initial_coordinates = None

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False

        # Replaced when agent is put in playground
        self.size_playground = (0, 0)

        # Keep track of the actions for display
        self.current_actions = None

        # Actuators
        self._actuators = []

        # Motor noise
        self._noise = False
        if noise_params is not None:
            self._noise = True
            self._noise_type = noise_params.get('type', 'gaussian')

            if self._noise_type == 'gaussian':
                self._noise_mean = noise_params.get('mean', 0)
                self._noise_scale = noise_params.get('scale', 1)

            else:
                raise ValueError('Noise type not implemented')

        self._controller = None

        # Reward
        self.reward = 0

        # Teleport
        self.is_teleporting = False

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping = False
        self._overlapping_strategy_set = False
        self._max_attempts = 100
        self._error_if_fails = False

    # CONTROLLER
    @property
    def controller(self):
        """
        The controller allows to select actions for each actuator of the agent.
        """
        return self._controller

    @controller.setter
    def controller(self, controller):

        self._controller = controller

        self._controller.controlled_actuators = self._actuators

        if self._controller.require_key_mapping:
            self._controller.discover_key_mapping()

        self.current_actions = controller.generate_null_actions()

    def add_actuator(self, actuator):

        self._actuators.append(actuator)
        if isinstance(actuator, Grasp):
            actuator.part.can_grasp = True

    # OVERLAPPING STRATEGY
    @property
    def overlapping_strategy(self):
        if self._overlapping_strategy_set:
            return self._allow_overlapping, self._max_attempts, self._error_if_fails

        else:
            return None

    @overlapping_strategy.setter
    def overlapping_strategy(self, strategy):
        self._allow_overlapping, self._max_attempts, self._error_if_fails = strategy
        self._overlapping_strategy_set = True


    # POSITION / VELOCITY
    @property
    def initial_coordinates(self):
        """
        Initial position can be fixed (tuple) or a PositionAreaSampler.
        """

        if isinstance(self._initial_position_angle, tuple):
            return self._initial_position_angle
        if isinstance(self._initial_position_angle, CoordinateSampler):
            return self._initial_position_angle.sample()

        return self._initial_position_angle

    @initial_coordinates.setter
    def initial_coordinates(self, coordinates):
        self._initial_position_angle = coordinates

    @property
    def coordinates(self):
        return self.base_platform.position, self.base_platform.angle

    @coordinates.setter
    def coordinates(self, coord):

        position, angle = coord

        for part in self.parts:
            if part is self.base_platform:
                part.position, part.angle = position, angle
            else:
                part.set_relative_coordinates()

    @property
    def position(self):
        """
        Position of the agent.
        In case of an Agent with multiple Parts, its position is the position of the base_platform.
        """
        return self.base_platform.position

    @position.setter
    def position(self, pos):
        self.coordinates = pos, self.angle

    @property
    def angle(self):
        """
        Angle of the agent.
        In case of an Agent with multiple Parts, its angle is the angle of the base_platform.
        Setter only used during initialization
        """
        return self.base_platform.angle

    @angle.setter
    def angle(self, theta):
        self.coordinates = self.position, theta

    @property
    def velocity(self):
        """
        Velocity of the agent.
        In case of an Agent with multiple Parts, its velocity is the velocity of the base_platform.
        """
        return self.base_platform.velocity

    @velocity.setter
    def velocity(self, velocity):
        for part in self.parts:
            part.velocity = velocity

    # SENSORS

    def add_sensor(self, new_sensor):
        """
        Add a Sensor to an agent.
        Should be done outside of a playground.
        Else, it will raise an error.

        Args:
            new_sensor: Sensor.

        Returns:

        """
        if self.in_a_playground:
            raise ValueError('Add sensors outside of a playground.')

        self.sensors.append(new_sensor)

    def generate_sensor_image(self, width_sensor=200, height_sensor=30, plt_mode=False):
        """
        Generate a full image containing all the sensor representations of an Agent.
        Args:
            width_sensor: width of the display for drawing.
            height_sensor: when applicable (1D sensor), the height of the display.
            plt_mode: if True, returns images compatible with pyplot.

        Returns:

        """

        list_sensor_images = []
        for sensor in self.sensors:
            list_sensor_images.append(sensor.draw(width_sensor, height_sensor))

        full_height = sum([im.shape[0] for im in list_sensor_images])\
                      + len(list_sensor_images) * (_BORDER_IMAGE + 1)

        full_img = np.ones((full_height, width_sensor, 3))

        current_height = 0
        for sensor_image in list_sensor_images:
            current_height += _BORDER_IMAGE
            full_img[current_height:sensor_image.shape[0] + current_height, :, :] \
                = sensor_image[:, :, :]
            current_height += sensor_image.shape[0]

        if plt_mode:
            full_img = full_img[:, :, ::-1]

        return full_img

    # BODY PARTS

    def add_body_part(self, part):
        """
        Add a Part to the agent
        Args:
            part: Part to add to the agent.

        """
        self.parts.append(part)

    def apply_actions_to_actuators(self, actions_dict):
        """
        Apply actions to each body part of the agent.

        Args:
            actions_dict: dictionary of body_part_name, Action.
        """

        if self._noise:
            self.current_actions = self._apply_noise(actions_dict)
        else:
            self.current_actions = actions_dict

        for actuator, value in actions_dict.items():
            actuator.apply_action(value)

    def _apply_noise(self, actions_dict):

        noisy_actions = {}

        if self._noise_type == 'gaussian':

            for actuator, value in actions_dict.items():

                if actuator.action_space is ActionSpaces.CONTINUOUS:

                    additive_noise = random.gauss(self._noise_mean, self._noise_scale)

                    new_value = additive_noise + value
                    new_value = new_value if new_value > actuator.min else actuator.min
                    new_value = new_value if new_value < actuator.max else actuator.max

                    noisy_actions[actuator] = new_value

                else:

                    noisy_actions[actuator] = value

        else:
            raise ValueError('Noise type not implemented')

        return noisy_actions

    def owns_shape(self, pm_shape):
        """
        Verifies if a pm_shape belongs to an agent.

        Args:
            pm_shape: pymunk_shape.

        Returns: True if pm_shape belongs to the agent.

        """
        all_shapes = [part.pm_visible_shape for part in self.parts]
        if pm_shape in all_shapes:
            return True
        return False

    def get_bodypart_from_shape(self, pm_shape):
        """
        Returns the body part that correspond to particular Pymunk shape.

        Args:
            pm_shape: pymunk shape.

        Returns: Body part.

        """
        return next(iter([part for part in self.parts if part.pm_visible_shape == pm_shape]), None)

    # DYNAMICS

    def pre_step(self):
        """
        Reset actuators and reward to 0 before a new step of the environment.
        """

        self.reward = 0
        self.is_teleporting = False

    def reset(self):
        """
        Resets all body parts
        """
        self.coordinates = self.initial_coordinates
        self.velocity = [0, 0]

    def draw(self, surface, excluded=None):
        """
        Draw the agent on a pygame surface.

        Args:
            surface: Pygame Surface to draw on.
            excluded: parts that should not be drawn on the surface.
        """

        if excluded is None:
            list_excluded = []
        else:
            list_excluded = excluded

        for part in self.parts:
            if part not in list_excluded:
                part.draw(surface, )

    def generate_actions_image(self, width_action=100, height_action=30, plt_mode=False):
        """
        Function that draws all action values of the agent.

        Args:
            width_action: width of the action image in pixels.
            height_action: height of a single action image in pixels.
            plt_mode: if True, returns a pyplot-compatible image.

        Returns:
            Image of the agent's current actions.

        """
        # pylint: disable=too-many-locals

        number_parts_with_actions = len(self.parts)
        count_all_actions = len(self.current_actions)

        total_height_actions = number_parts_with_actions * (_BORDER_IMAGE + height_action) \
                               + (_BORDER_IMAGE + height_action) * count_all_actions + _BORDER_IMAGE

        img_actions = Image.new("RGB", (total_height_actions, width_action), (255, 255, 255))
        drawer_action_image = ImageDraw.Draw(img_actions)

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", int(height_action * 2 / 3))

        current_height = 0

        for part in self.parts:

            w_text, h_text = fnt.getsize(text=part.name.upper())
            drawer_action_image.text((width_action / 2.0 - w_text/2, current_height + height_action/2 - h_text/2), part.name.upper(),
                   font=fnt, fill=(0, 0, 0))

            start = (0, current_height)
            end = (width_action, current_height + height_action)
            drawer_action_image.rectangle([start, end], outline=(0, 0, 0), width=2)

            current_height += _BORDER_IMAGE + height_action

            all_action_parts = [(action, value) for action, value in self.current_actions.items() if
                                action.part.name == part.name]

            for actuator, value in all_action_parts:

                actuator.draw(drawer_action_image, current_height, height_action, fnt)
                current_height += _BORDER_IMAGE + height_action

        img_actions = np.asarray(img_actions)/255.

        if plt_mode:
            img_actions = img_actions[:, :, ::-1]

        return img_actions
