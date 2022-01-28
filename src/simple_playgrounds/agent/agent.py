""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard controllers.

Examples can be found in simple_playgrounds/agents/agents.py

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple, Union

from gym.spaces import space
import numpy as np
from numpy.lib.function_base import append
from simple_playgrounds.agent.controller import Command, Controller

from simple_playgrounds.common.position_utils import (
    Coordinate,
    CoordinateSampler,
    InitCoord,
)
from simple_playgrounds.element.elements.teleport import TeleportElement
from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity
from simple_playgrounds.entity.embodied.physical import PhysicalEntity
from simple_playgrounds.entity.entity import Entity


if TYPE_CHECKING:
    from simple_playgrounds.agent.sensor.sensor import SensorDevice
    from simple_playgrounds.playground.playground import Commands

from simple_playgrounds.agent.part.part import Part

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
        temporary: Optional[bool] = False,
        **kwargs,
    ):

        super().__init__(**kwargs)
     
        self._name_count = {}
        self._name_to_controller = {}

        # Controllers
        self._controllers: List[Controller] = []

        # Body parts
        self._parts: List[Part] = []
        self._base = self._add_base(**kwargs)

        # List of sensors
        self._sensors: List[SensorDevice] = []

        # Reward
        self._reward: float = 0

        # Teleport
        self._teleported_to: Optional[Union[Coordinate,
                                            TeleportElement]] = None

        self._temporary = temporary

    def get_name(self, obj: Controller):
        index = self._name_count.get(type(obj), 0)
        self._name_count[type(obj)] = index + 1
        name = type(obj).__name__ + '_' + str(index)
        return name

    ################
    # Properties
    ################

    @property
    def position(self):
        return self._base.position

    @property
    def angle(self):
        return self._base.angle

    ################
    # Observations
    ################

    @property
    def observations(self):
        return {sens: sens.sensor_values for sens in self._sensors}

    @property
    def observation_space(self) -> Dict[SensorDevice, space.Space]:
        return {sens: sens.observation_space for sens in self._sensors}

    def compute_observations(self,
                             keys_are_str: bool = True,
                             return_np_arrays: bool = True):
        pass

    ################
    # Commands
    ################
    
    @property
    def parts(self):
        return self._parts

    @property
    def controllers(self) -> List[Controller]:
        return self._controllers

    @property
    def default_commands(self) -> Commands:
        return {controller: controller.default for controller in self._controllers}

    def apply_commands(self, commands: Commands):
        
        # Set command values
        if isinstance(commands, np.ndarray):
            for index, controller in enumerate(self.controllers):
                controller.set_command(commands[index])
            return

        for controller, command in commands.items():
            if isinstance(controller, str):
                controller = self._name_to_controller[controller]

            controller.set_command(command)

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

    @abstractmethod
    def _add_base(self, **kwargs) -> Part:
        """
        Create a base.
        This should pass the parameters for the base 
        and its initial position for when created.
        """
        ...

    def add_part(self, part: Part):
        if part in self._parts:
            raise ValueError('Part already in agent')

        self._parts.append(part)

        for controller in part.controllers:
            self._controllers.append(controller)
            self._name_to_controller[controller.name] = controller

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

    def reset(self):
        
        # Remove completely if temporary
        if self._temporary:
            self.remove()
            return
        
        self._removed = False
        for part in self._parts:
            part.reset()

    def post_step(self, **kwargs):
        
        for part in self._parts:
            part.post_step(**kwargs)

        for sensor in self._sensors:
            sensor.post_step(**kwargs)

    ###############
    # PLAYGROUND INTERACTIONS
    ###############

    def remove(self, definitive: Optional[bool] = True):
        for part in self._parts:
            part.remove(definitive=definitive)
        self._removed = True

        # self._playground.remove_from_mappings(self)

    def move_to(self,
                coord: Coordinate,
                keep_velocity: bool = True,
                keep_joints: bool = True):
        
        """
        After moving, the agent body is back in its original configuration.
        Default angle, etc.
        """

        position, angle = coord

        if keep_joints:
            relative_positions = {part: part.relative_position for part in self._parts}
            relative_angles = {part: part.relative_angle for part in self._parts}

        if not keep_joints and keep_velocity:
            relative_velocities = {part: part.relative_velocity for part in self._parts}
            relative_ang_velocities = {part: part.angular_velocity for part in self._parts}

        self._base.move_to(coord, keep_velocity=keep_velocity)

        for part in self._parts:
            if part is not self._base:
                coord = relative_positions[part], relative_angles[part]
                vel = relative_velocities[part], relative_ang_velocities[part]
                part.move_to(coord, velocity=vel)

    @property
    def teleported_to(self):
        return self._teleported_to

    @teleported_to.setter
    def teleported_to(self, destination):
        self._teleported_to = destination

    def _update_teleport(self):

        if isinstance(self._teleported_to, TeleportElement):
            if self._overlaps(self._teleported_to):
                return

        self._teleported_to = None

    def _overlaps(
        self,
        entity: EmbodiedEntity,
    ) -> bool:

        for part in self.parts:

            if entity.pm_shape and part.pm_shape.shapes_collide(entity.pm_shape).points:
                return True

            if entity.pm_shape and part.pm_shape.shapes_collide(entity.pm_shape).points:
                return True

        return False

    # @property
    # def grasped_elements(self):
    #     list_hold = []
    #     for part in self._parts:
    #         if isinstance(part, GraspPart):
    #             list_hold + part.grasped_elements
    #     return list_hold
   
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

