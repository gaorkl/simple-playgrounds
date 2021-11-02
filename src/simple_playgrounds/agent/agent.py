""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard commands.

Examples can be found in simple_playgrounds/agents/agents.py

"""
from __future__ import annotations

from typing import List, Optional, Dict, Union, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from simple_playgrounds.agents.sensors.sensor import SensorDevice
    from simple_playgrounds.agent.actuators import Actuator
    from simple_playgrounds.agent.controllers import Controller
    from pymunk import Shape
    from pygame import Surface
    from ..agents.communication import CommunicationDevice
    from simple_playgrounds.playgrounds.playground import Playground
    from simple_playgrounds.agents.parts.parts import Part, Platform, AnchoredPart

from abc import ABC
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..common.position_utils import CoordinateSampler, Coordinate
from simple_playgrounds.agent.actuators import Grasp
from simple_playgrounds.element.elements.teleport import TeleportElement

from simple_playgrounds.common.entity import Entity

# pylint: disable=too-many-instance-attributes
# pylint: disable=no-member

_BORDER_IMAGE = 3


class Agent(Entity, ABC):
    """
    Base class for building agents.
    Agents are composed of a base_platform and parts which are anchored with each other.
    Actuators are applied to parts to allow discrete or continuous control.
    Sensors can be anchored to parts of an agent.

    Attributes:
        name: name of the agent. Either provided by the user or generated using internal counter.
        base_platform: Main part of the agent. Can be mobile or fixed.
        _parts: Different parts attached to the base or to other parts.
        actuators:
        sensors:
        initial_coordinates:


    """

    def __init__(
        self,
        base_platform: Platform,
        **kwargs,
    ):
        """
        Base class for agents.

        Args:
            base_platform: Platform object, required to initialize an agent.
                All agents have a Platform.
            name: Name of the agent. If not provide, a name will be added by default.

        """

        Entity.__init__(**kwargs)

        # List of sensors
        self._sensors: List[SensorDevice] = []

        # Base Platform
        self.base_platform: Platform = base_platform
        base_platform.agent = self

        self._parts: List[Part] = [self.base_platform]

        # Default starting position
        self.initial_coordinates: Optional[Union[Coordinate,
                                                 CoordinateSampler]] = None

        # Keep track of the actions for display
        self._current_actions: Optional[Dict[Actuator, float]] = None

        # Actuators
        self._actuators: List[Actuator] = []
        self._controller: Optional[Controller] = None

        # Reward
        self.acquired_reward: float = 0

        # Teleport
        self._teleported_to: Optional[Coordinate, TeleportElement] = None
        self._has_teleported: bool = False

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping: bool = False
        self._overlapping_strategy_set: bool = False
        self._max_attempts: int = 100

        # Communication
        self._communication: Optional[CommunicationDevice] = None

    def _add_to_playground(self):

        for part in self._parts:
            part.add_to_playground(self._playground)

        if self._communication:
            self._communication.add_to_playground(self.playground)

        for sensor in self._sensors:
            sensor.add_to_playground(self.playground)

    def _remove_from_playground(self):

        for part in self._parts:
            part.remove_from_playground()

        if self._communication:
            self._communication.remove_from_playground()

        for sensor in self._sensors:
            sensor.remove_from_playground()

    def add(self,
            entity: Union[Part, CommunicationDevice, SensorDevice],
            **kwargs):

        if isinstance(entity, CommunicationDevice):
            if self._communication:
                raise ValueError("Communication already added")
            self._add_communication_device(entity)

        elif isinstance(entity, Part):
            self._add_part(entity, anchor=anchor, **kwargs)

        elif isinstance(entity, SensorDevice):
            self._add_sensor_devices(entity, anchor=anchor, **kwargs)

    def _add_communication_devices(self, comm: CommunicationDevice, anchor: Part, **kwargs):

        self.attach_device_to_anchor()
        comm.add_to_playground(self._playground)

        self._playground._communication_devices.append(comm)

    def _add_part(self, part: Part, anchor: Part, **kwargs):

        self._parts.append(part)
        self.attach_part_to_anchor(anchor, **kwargs)
        part.agent = self
        part.add_to_playground(self._playground)

    def _add_sensor_device(self, sensor: SensorDevice, anchor: Part, ):

        # Set the invisible element filters
        for sensor in agent._sensors:

            self._sensor_devices.append(sensor)
            self._space.add(sensor.pm_shape)

            sensor.set_playground_size(self.size)


    def remove_from_playground(self):

        for part in agent._parts:
            self.space.remove(*part.pm_elements)

        if agent.can_communicate:
            self._communication_devices.remove(agent.communication)
            self.space.remove(agent.communication.pm_shape)

        for sensor in agent._sensors:
            self._sensor_devices.remove(sensor)
            self.space.remove(sensor.pm_shape)

        self.agents.remove(agent)
        assert not agent.in_playground



    @property
    def can_communicate(self):
        return bool(self._communication)

    @property
    def communication(self):
        return self._communication

    def add_to_playground(self, playground: Playground):



        self._add_to_playground(playground)
        self._playground = playground

    def remove_from_playground(self):
        self._remove_from_playground()
        self._playground = None


    def add_to_playground(self, playground):

        self._add_sensor_devices(playground)
        self._add_communication_devices(playground)





    # COMMUNICATION
    def add_communication(self,
                          communication: CommunicationDevice,
                          ):

        if self.in_playground:
            raise ValueError('Add Communication outside of a playground.')

        if self._can_communicate:
            raise ValueError('Communication Device already added')

        self.communication = communication
        self._can_communicate = True

    @property
    def can_communicate(self):
        return self._can_communicate

    # CONTROLLER
    @property
    def controller(self):
        """
        The controller allows to select actions for each actuator of the agent.
        """
        return self._controller

    @controller.setter
    def controller(self, controller: Controller):

        self._controller = controller
        self._controller.controlled_actuators = self._actuators
        self._current_actions = controller.generate_null_actions()

    def add_actuator(self, actuator: Actuator):
        self._actuators.append(actuator)

    @property
    def grasped_elements(self):

        list_hold = []

        for act in self._actuators:
            if isinstance(act, Grasp) and act.grasped_element:
                list_hold.append(act.grasped_element)

        return list_hold

    # OVERLAPPING STRATEGY
    @property
    def overlapping_strategy(self):
        if self._overlapping_strategy_set:
            return self._allow_overlapping, self._max_attempts
        return None

    @overlapping_strategy.setter
    def overlapping_strategy(
        self,
        strategy: Tuple[bool, int],
    ):
        self._allow_overlapping, self._max_attempts = strategy
        self._overlapping_strategy_set = True

    # POSITION / VELOCITY
    @property
    def initial_coordinates(self):
        """
        Initial position can be fixed (tuple) or a PositionAreaSampler.
        """

        if isinstance(self._initial_coordinates, tuple):
            return self._initial_coordinates
        if isinstance(self._initial_coordinates, CoordinateSampler):
            return self._initial_coordinates.sample()

        return self._initial_coordinates

    @initial_coordinates.setter
    def initial_coordinates(self, coordinates: Union[Coordinate,
                                                     CoordinateSampler]):
        self._initial_coordinates = coordinates

    @property
    def coordinates(self):
        return self.base_platform.position, self.base_platform.angle

    @coordinates.setter
    def coordinates(self, coord: Coordinate):

        position, angle = coord

        for part in self._parts:
            if isinstance(part, Platform):
                part.position, part.angle = position, angle
            elif isinstance(part, AnchoredPart):
                part.set_relative_coordinates()
            else:
                raise ValueError("Part type not implemented")

    def reindex_shapes(self):

        for part in self._parts:
            part.pm_body.space.reindex_shapes_for_body(part.pm_body)

    @property
    def position(self):
        """
        Position of the agent.
        In case of an Agent with multiple Parts, its position is the position of the base_platform.
        """
        return self.base_platform.position

    @position.setter
    def position(self, pos: Tuple[float, float]):
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
    def angle(self, theta: float):
        self.coordinates = self.position, theta

    @property
    def velocity(self):
        """
        Velocity of the agent.
        In case of an Agent with multiple Parts, its velocity is the velocity of the base_platform.
        """
        return self.base_platform.velocity

    @velocity.setter
    def velocity(self, velocity: Tuple[float, float]):
        for part in self._parts:
            part.velocity = velocity

    @property
    def angular_velocity(self):
        """
        Velocity of the agent.
        In case of an Agent with multiple Parts, its velocity is the velocity of the base_platform.
        """
        return self.base_platform.angular_velocity

    @angular_velocity.setter
    def angular_velocity(
        self,
        angular_velocity: float,
    ):
        for part in self._parts:
            part.angular_velocity = angular_velocity

    # SENSORS

    def add_sensor(self, new_sensor: SensorDevice):
        """
        Add a Sensor to an agent.
        Should be done outside of a playground.
        Else, it will raise an error.

        Args:
            new_sensor: Sensor.

        Returns:

        """
        if self.in_playground:
            raise ValueError('Add sensors outside of a playground.')

        self._sensors.append(new_sensor)

    @property
    def in_playground(self) -> bool:

        if self.base_platform.pm_body.space:
            return True
        return False

    @property
    def observations(self):
        return {sensor: sensor.sensor_values for sensor in self._sensors}

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


    def apply_actions_to_actuators(self, actions_dict: Dict[Actuator, float]):
        """
        Apply actions to each body part of the agent.

        Args:
            actions_dict: dictionary of body_part_name, Action.
        """

        self._current_actions = actions_dict

        for actuator, value in actions_dict.items():
            actuator.apply_action(value)

    def owns_shape(self, pm_shape: Shape):
        """
        Verifies if a pm_shape belongs to an agent.

        Args:
            pm_shape: pymunk_shape.

        Returns: True if pm_shape belongs to the agent.

        """
        all_shapes = [part.pm_visible_shape for part in self._parts]
        if pm_shape in all_shapes:
            return True
        return False

    def get_part_from_shape(self, pm_shape: Shape):
        """
        Returns the body part that correspond to particular Pymunk shape.

        Args:
            pm_shape: pymunk shape.

        Returns: Body part.

        """
        return next(
            iter([
                part for part in self._parts
                if part.pm_visible_shape == pm_shape
            ]), None)

    # DYNAMICS

    @property
    def teleported_to(self):
        return self._teleported_to

    def has_teleported_to(self, destination):
        self._teleported_to = destination
        self._has_teleported = True

    @property
    def has_teleported(self):
        return self._has_teleported

    def pre_step(self):
        """
        Reset actuators and reward to 0 before a new step of the environment.
        """

        self.acquired_reward = 0

        # If the agent is outside of the range of the teleport it arrived on,
        # it can again use the teleport.

        self._update_teleport()

        for actuator in self._actuators:
            actuator.pre_step()

    def _update_teleport(self):

        self._has_teleported = False

        if isinstance(self._teleported_to, TeleportElement):
            if self._overlaps(self._teleported_to):
                return

        self._teleported_to = None



    def _overlaps(
        self,
        entity: Entity,
    ) -> bool:

        for part in self._parts:

            if entity.pm_visible_shape and part.pm_visible_shape.shapes_collide(entity.pm_visible_shape):
                return True

            if entity.pm_invisible_shape and part.pm_visible_shape.shapes_collide(entity.pm_invisible_shape):
                return True

        return False

    def reset(self):
        """
        Resets all body parts
        """
        self.velocity = [0, 0]

        for part in self._parts:
            part.reset()

    def draw(self,
             surface: Surface,
             excluded: Optional[Union[List[Entity], Entity]] = None):
        """
        Draw the agent on a pygame surface.

        Args:
            surface: Pygame Surface to draw on.
            excluded: parts that should not be drawn on the surface.
        """

        if not excluded:
            list_excluded = []
        elif not isinstance(excluded, list):
            list_excluded = [excluded]
        else:
            list_excluded = excluded

        for part in self._parts:
            if part not in list_excluded:
                part.draw(surface, )

    def generate_actions_image(self,
                               width_action: int = 100,
                               height_action: int = 30,
                               plt_mode: bool = False):
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

        number_parts_with_actions = len(self._parts)

        assert isinstance(self._current_actions, dict)
        count_all_actions = len(self._current_actions)

        total_height_actions = number_parts_with_actions * (_BORDER_IMAGE + height_action) \
                               + (_BORDER_IMAGE + height_action) * count_all_actions + _BORDER_IMAGE

        img_actions = Image.new("RGB", (width_action, total_height_actions),
                                (255, 255, 255))
        drawer_action_image = ImageDraw.Draw(img_actions)

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf",
                                 int(height_action * 2 / 3))

        current_height = 0

        for part in self._parts:

            w_text, h_text = fnt.getsize(text=part.name.upper())
            drawer_action_image.text(
                (width_action / 2.0 - w_text / 2,
                 current_height + height_action / 2 - h_text / 2),
                part.name.upper(),
                font=fnt,
                fill=(0, 0, 0))

            start = (0, current_height)
            end = (width_action, current_height + height_action)
            drawer_action_image.rectangle([start, end],
                                          outline=(0, 0, 0),
                                          width=2)

            current_height += _BORDER_IMAGE + height_action

            all_action_parts = [
                (action, value)
                for action, value in self._current_actions.items()
                if action.part.name == part.name
            ]

            for actuator, _ in all_action_parts:

                actuator.draw(drawer_action_image, width_action,
                              current_height, height_action, fnt)
                current_height += _BORDER_IMAGE + height_action

        img_actions = np.asarray(img_actions) / 255.

        if plt_mode:
            img_actions = img_actions[:, :, ::-1]

        return img_actions

