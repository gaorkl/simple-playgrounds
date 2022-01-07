""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard commands.

Examples can be found in simple_playgrounds/agents/agents.py

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple, Union

from gym.spaces import space
import numpy as np
from simple_playgrounds.agent.command import Command

from simple_playgrounds.common.position_utils import (
    Coordinate,
    CoordinateSampler,
    InitCoord,
)
from simple_playgrounds.element.elements.teleport import TeleportElement
from simple_playgrounds.entity.embodied.physical import PhysicalEntity


if TYPE_CHECKING:
    from simple_playgrounds.agent.sensor.sensor import SensorDevice
    
from simple_playgrounds.agent.part.part import Part

_BORDER_IMAGE = 3


class Agent(Part, ABC):
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
        """
        Base class for agents.

        Args:
            base_platform: Platform object, required to initialize an agent.
                All agents have a Platform.
            name: Name of the agent. 
                If not provide, a name will be added by default.

        """
        super().__init__(**kwargs)

        # List of sensors
        self._sensors: List[SensorDevice] = []

        # Body parts
        self._parts: List[Part] = []

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._initial_coordinate_sampler: Optional[CoordinateSampler] = None
        self._allow_overlapping = True

        # Reward
        self._reward: float = 0

        # Teleport
        self._teleported_to: Optional[Union[Coordinate,
                                            TeleportElement]] = None

    @property
    def parts(self):
        return self._parts

    ################
    # Observations
    ################

    @property
    def observations(self):
        obs = {}
        for sens in self._sensors:
            obs[sens] = sens.update()
        return obs

    @property
    def observation_space(self) -> Dict[SensorDevice, space.Space]:
        return {sens: sens.observation_space for sens in self._sensors}

    ################
    # Commands 
    ################

    @property
    def commands(self) -> List[Command]:
        return [command for part in self._parts for command in part.commands]

    @property
    def default_commands(self):
        return {command: command.default for command in self.commands}

    @property
    def random_commands(self):
        return {command: command.sample for command in self.commands}

    ################
    # Rewards
    ################

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def reindex_shapes(self):
        for part in self._parts:
            part.reindex_shapes()

    #############
    # ADD PARTS AND SENSORS 
    #############

    def add(self, component: Union[SensorDevice, Part]):

        if isinstance(component, SensorDevice):
            self._sensors.append(component)

        elif isinstance(component, Part):
            self._parts.append(component)

        else:
            raise ValueError('Not Implemented')

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

        for sensor in self._sensors:
            sensor.pre_step(**kwargs)

    def step(self, **kwargs):

        for part in self._parts:
            part.step(**kwargs)

    def reset(self):
        for part in self._parts:
            part.reset()

    ###############
    # PLAYGROUND INTERACTIONS
    ###############
 
    def move(self, coord: Coordinate):

        position, angle = coord

        for part in self._parts:
            if isinstance(part, Platform):
                part.position, part.angle = position, angle
            elif isinstance(part, AnchoredPart):
                part.set_relative_coordinates()
            else:
                raise ValueError("Part type not implemented")


    @property
    def teleported_to(self):
        return self._teleported_to

    def has_teleported_to(self, destination):
        self._teleported_to = destination
        self._has_teleported = True

    @property
    def has_teleported(self):
        return self._has_teleported

    def _update_teleport(self):

        self._has_teleported = False

        if isinstance(self._teleported_to, TeleportElement):
            if self._overlaps(self._teleported_to):
                return

        self._teleported_to = None
 
    @property
    def grasped_elements(self):
        list_hold = []
        for part in self._parts:
            list_hold.append(part.grasped_elements)
        return list_hold
   

    def _overlaps(
        self,
        entity: Entity,
    ) -> bool:

        for part in self.parts:

            if entity.pm_visible_shape and part.pm_visible_shape.shapes_collide(entity.pm_visible_shape):
                return True

            if entity.pm_invisible_shape and part.pm_visible_shape.shapes_collide(entity.pm_invisible_shape):
                return True

        return False

    def generate_sensor_image(self,
                              width_sensor: int = 200,
                              height_sensor: int = 30,
                              plt_mode: bool = False):
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

        full_height = sum([im.shape[0] for im in list_sensor_images]) \
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

