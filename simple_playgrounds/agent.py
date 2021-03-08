"""
Module for Agent Class.
"""
import random
import numpy as np
import cv2

from simple_playgrounds.utils.definitions import ActionTypes
from simple_playgrounds.utils.position_utils import PositionAreaSampler

# pylint: disable=too-many-instance-attributes
# pylint: disable=no-member

BORDER_IMAGE = 3
FONT_TEXT = cv2.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (0, 0, 0)
FONT_SCALE = 0.5


class Agent:
    """
    Base class for agents

    """
    index_agent = 0

    def __init__(self, base_platform, initial_position=None, name=None, noise_params=None):
        """
        Base class for agents.

        Args:
            base_platform: Platform object, required to initialize an agent.
                All agents have a Platform.
            initial_position: initial position of the base of the agent.
                Can be tuple, or PositionAreaSampler.
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
        self.initial_position = initial_position

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False

        # Replaced when agent is put in playground
        self.size_playground = (0, 0)

        # Keep track of the actions for display
        self.current_actions = None

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

        self._controller.controlled_actuators = self.get_all_actuators()

        if self._controller.require_key_mapping:
            self._controller.discover_key_mapping()

        self.current_actions = controller.generate_null_actions()

    # POSITION / VELOCITY

    @property
    def initial_position(self):
        """
        Initial position can be fixed (tuple) or a PositionAreaSampler.
        """

        if isinstance(self._initial_position, tuple):
            return self._initial_position
        if isinstance(self._initial_position, PositionAreaSampler):
            return self._initial_position.sample()

        return self._initial_position

    @initial_position.setter
    def initial_position(self, position):
        self._initial_position = position

    @property
    def position_np(self):
        """
        Position of the agent in numpy coordinate system.
        """
        return self.base_platform.position_np

    @property
    def position(self):
        """
        Position of the agent.
        In case of an Agent with multiple Parts, its position is the position of the base_platform.
        """
        return self.base_platform.position

    @position.setter
    def position(self, position):

        for part in self.parts:
            if part is self.base_platform:
                part.position = position
            else:
                part.set_relative_position()

    @property
    def velocity_np(self):
        """
        Velocity of the agent in numpy coordinate system.
        """
        return self.base_platform.velocity_np

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

    @property
    def relative_velocity(self):
        """
        Velocity of the agent from the point of view of the agent.
        In case of an Agent with multiple Parts, its velocity is the velocity of the base_platform.
        """
        return self.base_platform.relative_velocity

    @property
    def size_playground(self):
        """
        Size of the Playground where agents are playing.
        """
        return self.size_playground

    @size_playground.setter
    def size_playground(self, size_pg):
        self._size_playground = size_pg
        for part in self.parts:
            part.size_playground = size_pg

    # SENSORS

    def add_sensor(self, new_sensor):
        """
        Add a Sensor to an agent.

        Args:
            new_sensor: Sensor.

        Returns:

        """
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

        border = 5

        list_sensor_images = []
        for sensor in self.sensors:
            list_sensor_images.append(sensor.draw(width_sensor, height_sensor))

        full_height = sum([im.shape[0] for im in list_sensor_images])\
                      + len(list_sensor_images) * (border + 1)

        full_img = np.ones((full_height, width_sensor, 3))

        current_height = 0
        for sensor_image in list_sensor_images:
            current_height += border
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

    def get_all_actuators(self):
        """
        Computes all the available actions of the agent.

        Returns: List of available actions.
        """

        actuators = []
        for part in self.parts:
            actuators = actuators + part.actuators

        return actuators

    def apply_actions_to_body_parts(self, actions_dict):
        """
        Apply actions to each body part of the agent.

        Args:
            actions_dict: dictionary of body_part_name, Action.
        """

        if self._noise:
            self.current_actions = self._apply_noise(actions_dict)
        else:
            self.current_actions = actions_dict

        for actuator, value in self.current_actions.items():

            for body_part in self.parts:
                body_part.apply_action(actuator, value)

    def _apply_noise(self, actions_dict):

        noisy_actions = {}

        if self._noise_type == 'gaussian':

            for actuator, value in actions_dict.items():
                additive_noise = random.gauss(self._noise_mean, self._noise_scale)
                new_value = additive_noise + value
                new_value = new_value if new_value > actuator.min else actuator.min
                new_value = new_value if new_value < actuator.max else actuator.max

                noisy_actions[actuator] = new_value

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
        self.position = self.initial_position
        self.velocity = [0, 0, 0]

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

        total_height_actions = number_parts_with_actions * (BORDER_IMAGE + height_action) \
                               + (BORDER_IMAGE + height_action) * count_all_actions + BORDER_IMAGE
        img_actions = np.ones((total_height_actions, width_action, 4))

        offset_string_name = int(height_action / 2.0 - FONT_SCALE * 10)

        action_names_length = max([len(action.action.name)
                                   for action, value in self.current_actions.items()])
        font_scale_action = 0.95 * width_action / action_names_length * 0.5 / 10
        offset_string_action = int(height_action / 2.0 - font_scale_action * 10)

        current_height = BORDER_IMAGE

        for part in self.parts:

            current_height += height_action

            start_box = int(width_action / 2.0 - 18 * FONT_SCALE * len(part.name) / 2)
            bottom_left = (start_box, current_height - offset_string_name)

            cv2.putText(img_actions, part.name.upper(),
                        bottom_left,
                        FONT_TEXT,
                        FONT_SCALE,
                        FONT_COLOR,
                        1)

            cv2.rectangle(img_actions, (0, current_height),
                          (width_action, current_height - height_action), (0, 0, 0), 3)

            current_height += BORDER_IMAGE

            all_action_parts = [(action, value) for action, value in self.current_actions.items() if
                                action.part_name == part.name]

            for action, value in all_action_parts:

                current_height += height_action

                if action.action_range == ActionTypes.DISCRETE and value == action.max:

                    cv2.rectangle(img_actions,
                                  (0, current_height),
                                  (width_action, current_height - height_action),
                                  (0.2, 0.6, 0.2, 0.1),
                                  -1)

                elif action.action_range == ActionTypes.CONTINUOUS_CENTERED and value != 0:

                    if value < 0:
                        left = int(width_action / 2. + value * width_action / 2.)
                        right = int(width_action / 2.)
                    else:
                        right = int(width_action / 2. + value * width_action / 2.)
                        left = int(width_action / 2.)

                    cv2.rectangle(img_actions,
                                  (left, current_height),
                                  (right, current_height - height_action),
                                  (0.2, 0.6, 0.2, 0.1),
                                  -1)

                elif action.action_range == ActionTypes.CONTINUOUS_NOT_CENTERED and value != 0:

                    left = int(width_action / 2.)
                    right = int(width_action / 2. + value * width_action / 2.)

                    cv2.rectangle(img_actions, (left, current_height),
                                  (right, current_height - height_action), (0.2, 0.6, 0.2, 0.1), -1)

                start_box = int(width_action / 2.0
                                - 18 * font_scale_action * len(action.action.name) / 2.)
                bottom_left = (start_box, current_height - offset_string_action)

                cv2.putText(img_actions, action.action.name.upper(),
                            bottom_left,
                            FONT_TEXT,
                            font_scale_action,
                            FONT_COLOR,
                            1)

                current_height += BORDER_IMAGE

        img_actions = cv2.cvtColor(img_actions.astype('float32'), cv2.COLOR_RGBA2BGR)

        if plt_mode:
            img_actions = img_actions[:, :, ::-1]

        return img_actions
