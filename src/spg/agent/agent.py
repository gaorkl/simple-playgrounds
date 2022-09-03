""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard controllers.

Examples can be found in spg/agents/agents.py

"""
from __future__ import annotations
from abc import abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING, Union

from gym.spaces import space
import numpy as np

from .controller import Controller

from ..utils.position import Coordinate
from ..entity import EmbodiedEntity, Entity

from ..element import Teleporter

if TYPE_CHECKING:
    from .sensor import Sensor
    from .controller import Commands
    from .interactor import Interactor
    from .communicator import Communicator

from .part import PhysicalPart

_BORDER_IMAGE = 3


class Agent(Entity):

    """
    Base class for building agents.
    Agents are composed of a base and parts which are attached to the base
    or to each other.
    Each part has actuators allowing for control of the agent.
    The base has no actuator.

    Attributes:
        name: name of the agent.
            Either provided by the user or generated using internal counter.
        base: Main part of the agent. Can be mobile or fixed.
        parts: Different parts attached to the base or to other parts.
        actuators:
        sensors:
        initial_coordinates:
    """

    _index_agent: int = 0

    def __init__(
        self,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self._name_count = {}
        self._name_to_controller = {}

        # Body parts
        self._parts: List[PhysicalPart] = []

        # Reward
        self._reward: float = 0

        # Teleport
        self._teleported_to: Optional[Union[Coordinate, Teleporter]] = None

        self._initial_coordinates = None
        self._allow_overlapping = False

    def add(self, part: PhysicalPart):
        part.agent = self
        part.teams = self._teams

        for device in part.devices:
            device.teams = self._teams

        self._parts.append(part)

    ################
    # Properties
    ################

    @property
    def base(self):
        return self._parts[0]

    @property
    def initial_coordinates(self):
        return self._initial_coordinates

    @initial_coordinates.setter
    def initial_coordinates(self, init_coord):
        self._initial_coordinates = init_coord
        self._parts[0].initial_coordinates = init_coord

    @property
    def allow_overlapping(self):
        return self._allow_overlapping

    @allow_overlapping.setter
    def allow_overlapping(self, allow):
        self._allow_overlapping = allow
        self._parts[0].allow_overlapping = allow

    @property
    def position(self):
        return self.base.position

    @property
    def angle(self):
        return self.base.angle

    ################
    # Observations
    ################

    @property
    def observations(self):
        return {
            sens: sens.sensor_values
            for part in self._parts
            for sens in part.devices
            if isinstance(sens, Sensor)
        }

    @property
    def observation_space(self) -> Dict[Sensor, space.Space]:
        return {
            sens: sens.observation_space
            for part in self._parts
            for sens in part.devices
            if isinstance(sens, Sensor)
        }

    @property
    def controllers(self):
        return [
            contr
            for part in self._parts
            for contr in part.devices
            if isinstance(contr, Controller)
        ]

    @property
    def sensors(self):
        return [
            sensor
            for part in self._parts
            for sensor in part.devices
            if isinstance(sensor, Sensor)
        ]

    def compute_observations(
        self, keys_are_str: bool = True, return_np_arrays: bool = True
    ):

        # For sensor in sensors:
        # test if view has been updated withon sensors
        # calculate observation
        # return dict of Sensor:SensorValue

        pass

    def compute_rewards(self):
        pass

    ################
    # Commands
    ################

    @property
    def parts(self):
        return self._parts

    @property
    def default_commands(self) -> Commands:
        return {controller: controller.default for controller in self.controllers}

    def receive_commands(self, commands: Commands):

        # Set command values
        if isinstance(commands, np.ndarray):
            for index, controller in enumerate(self.controllers):
                controller.command = commands[index]
            return

        for controller, command in commands.items():
            if isinstance(controller, str):
                controller = self._name_to_controller[controller]

            controller.command = command

    def apply_commands(self):
        # Apply command to playground physics
        for part in self._parts:
            part.apply_commands()

    ################
    # Rewards
    ################

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    #############
    # ADD PARTS AND SENSORS
    #############

    def update_team_filter(self):
        for part in self._parts:
            part.update_team_filter()

    ##############
    # CONTROL
    ##############

    def pre_step(self, **kwargs):
        """
        Reset actuators and reward to 0 before a new step of the environment.
        """

        self._reward = 0
        self._update_teleport(**kwargs)

        for part in self._parts:
            part.pre_step(**kwargs)

    def reset(self):
        for part in self._parts:
            part.reset()

    def post_step(self, **kwargs):
        for part in self._parts:
            part.post_step(**kwargs)

    ###############
    # PLAYGROUND INTERACTIONS
    ###############

    def move_to(self, coord: Coordinate, **kwargs):

        """
        After moving, the agent body is back in its original configuration.
        Default angle, etc.
        """
        self.base.move_to(coordinates=coord, move_anchors=True, **kwargs)

    @property
    def teleported_to(self):
        return self._teleported_to

    @teleported_to.setter
    def teleported_to(self, destination):
        self._teleported_to = destination

    def _update_teleport(self):

        if isinstance(self._teleported_to, Teleporter):
            if self._overlaps(self._teleported_to):
                return

        self._teleported_to = None

    def _overlaps(
        self,
        entity: EmbodiedEntity,
    ) -> bool:

        for part in self.parts:

            if self._playground.overlaps(part, entity):
                return True

        return False

    # @property
    # def grasped_elements(self):
    #     list_hold = []
    #     for part in self._parts:
    #         if isinstance(part, GraspPart):
    #             list_hold + part.grasped_elements
    #     return list_hold

    def generate_sensor_image(
        self, width_sensor: int = 200, height_sensor: int = 30, plt_mode: bool = False
    ):
        """
        Generate a full image containing all the sensor representations of an Agent.
        Args:
            width_sensor: width of the display for drawing.
            height_sensor: when applicable (1D sensor), the height of the display.
            plt_mode: if True, returns images compatible with pyplot.

        Returns:

        """

        list_sensor_images = []
        for sensor in self._sensors:
            list_sensor_images.append(sensor.draw(width_sensor, height_sensor))

        full_height = sum([im.shape[0] for im in list_sensor_images]) + len(
            list_sensor_images
        ) * (_BORDER_IMAGE + 1)

        full_img = np.ones((full_height, width_sensor, 3))

        current_height = 0
        for sensor_image in list_sensor_images:
            current_height += _BORDER_IMAGE
            full_img[
                current_height : sensor_image.shape[0] + current_height, :, :
            ] = sensor_image[:, :, :]
            current_height += sensor_image.shape[0]

        if plt_mode:
            full_img = full_img[:, :, ::-1]

        return full_img

    # def generate_actions_image(self, **kwargs):
    #     """
    #     Function that draws all action values of the agent.

    #     Args:
    #         width_action: width of the action image in pixels.
    #         height_action: height of a single action image in pixels.
    #         plt_mode: if True, returns a pyplot-compatible image.

    #     Returns:
    #         Image of the agent's current actions.

    #     """
    #     # pylint: disable=too-many-locals

    #     all_action_images = []

    #     for part in self._parts:
    #         img_action = part.draw_action(**kwargs)

    #     number_parts_with_actions = len(self._parts)

    #     assert isinstance(self._current_actions, dict)
    #     count_all_actions = len(self._current_actions)

    #     total_height_actions = number_parts_with_actions * (_BORDER_IMAGE + height_action) \
    #                            + (_BORDER_IMAGE + height_action) * count_all_actions + _BORDER_IMAGE

    #     img_actions = Image.new("RGB", (width_action, total_height_actions),
    #                             (255, 255, 255))
    #     drawer_action_image = ImageDraw.Draw(img_actions)

    #     fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf",
    #                              int(height_action * 2 / 3))

    #     current_height = 0

    #     for part in self.parts:

    #         w_text, h_text = fnt.getsize(text=part.name.upper())
    #         drawer_action_image.text(
    #             (width_action / 2.0 - w_text / 2,
    #              current_height + height_action / 2 - h_text / 2),
    #             part.name.upper(),
    #             font=fnt,
    #             fill=(0, 0, 0))

    #         start = (0, current_height)
    #         end = (width_action, current_height + height_action)
    #         drawer_action_image.rectangle([start, end],
    #                                       outline=(0, 0, 0),
    #                                       width=2)

    #         current_height += _BORDER_IMAGE + height_action

    #         all_action_parts = [
    #             (action, value)
    #             for action, value in self._current_actions.items()
    #             if action.part.name == part.name
    #         ]

    #         for actuator, _ in all_action_parts:

    #             actuator.draw(drawer_action_image, width_action,
    #                           current_height, height_action, fnt)
    #             current_height += _BORDER_IMAGE + height_action

    #     img_actions = np.asarray(img_actions) / 255.

    #     if plt_mode:
    #         img_actions = img_actions[:, :, ::-1]

    #     return img_actions

    # def generate_sensor_image(self,
    #                           width_sensor: int = 200,
    #                           height_sensor: int = 30,
    #                           plt_mode: bool = False):
    #     """
    #     Generate a full image containing all the sensor representations of an Agent.
    #     Args:
    #         width_sensor: width of the display for drawing.
    #         height_sensor: when applicable (1D sensor), the height of the display.
    #         plt_mode: if True, returns images compatible with pyplot.

    #     Returns:

    #     """

    #     list_sensor_images = []
    #     for sensor in self.sensors:
    #         list_sensor_images.append(sensor.draw(width_sensor, height_sensor))

    #     full_height = sum([im.shape[0] for im in list_sensor_images])\
    #                   + len(list_sensor_images) * (_BORDER_IMAGE + 1)

    #     full_img = np.ones((full_height, width_sensor, 3))

    #     current_height = 0
    #     for sensor_image in list_sensor_images:
    #         current_height += _BORDER_IMAGE
    #         full_img[current_height:sensor_image.shape[0] + current_height, :, :] \
    #             = sensor_image[:, :, :]
    #         current_height += sensor_image.shape[0]

    #     if plt_mode:
    #         full_img = full_img[:, :, ::-1]

    #     return full_img
