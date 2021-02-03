"""
Module for Agent Class.
"""
from .utils.definitions import SensorModality
from .utils.position_utils import PositionAreaSampler

#pylint: disable=too-many-instance-attributes


class Agent:
    """
    Base class for agents

    """
    index_agent = 0

    def __init__(self, initial_position, base_platform, **agent_params):
        """
        Base class for agents.

        Args:
            initial_position: initial position of the base
            base_platform: Platform object, required to initialize an agent.
                All agents have a Platform.
            **agent_param: other parameters
        """

        self.name = agent_params.get('name', None)

        if self.name is None:
            self.name = 'agent_' + str(Agent.index_agent)
        Agent.index_agent += 1

        # Dictionary for sensors
        self.sensors = []

        # Body parts
        self.base_platform = base_platform
        self.parts = [self.base_platform]

        # List of Actuators
        self.actuators = {}

        self.reward = 0
        self.energy_spent = 0

        # Default starting position
        self.initial_position = initial_position

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False

        # Replaced when agent is put in playground
        self.size_playground = [0, 0]

        # By default, and agent can start at an overlapping position
        self.allow_overlapping = agent_params.get('allow_overlapping', True)

        # Keep track of the actions for display
        self.current_actions = self.get_all_actuators()


    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, contr):

        self._controller = contr

        self.controller.controlled_actuators = self.get_all_actuators()

        if self._controller.require_key_mapping:
            self._controller.discover_key_mapping()

    def print_key_map(self):
        if self._controller:
            print(self._controller.key_map)

    # @property
    # def key_mapping(self):
    #     """
    #     A key mapping links keyboard strokes with actions.
    #     Necessary when the Agent is controlled by Keyboard Controller.
    #     """
    #     return None

    @property
    def initial_position(self):
        """
        Initial position can be fixed (list, tuple) or a PositionAreaSampler.
        """

        if isinstance(self._initial_position, (list, tuple)):
            return self._initial_position
        if isinstance(self._initial_position, PositionAreaSampler):
            return self._initial_position.sample()

        return self._initial_position

    @initial_position.setter
    def initial_position(self, position):
        self._initial_position = position

    @property
    def position_np(self):
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

    def add_sensor(self, new_sensor):
        """
        Add a Sensor to an agent.

        Args:
            new_sensor: Sensor.

        Returns:

        """
        if new_sensor.sensor_modality == SensorModality.SEMANTIC:
            self.has_geometric_sensor = True
        elif new_sensor.sensor_modality == SensorModality.VISUAL:
            self.has_visual_sensor = True

        self.sensors.append(new_sensor)

    def add_body_part(self, part):
        """
        Add a Part to the agent
        Args:
            part: Part to add to the agent.

        """
        part.part_number = len(self.parts)
        self.parts.append(part)

    def get_bodypart_from_shape(self, pm_shape):
        #pylint: disable=line-too-long
        return next(iter([part for part in self.parts if part.pm_visible_shape == pm_shape]), None)

    def assign_controller(self, controller):
        """
        Assigns a Controller to the agent
        """
        self.controller = controller

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

    def _find_part_by_name(self, body_part_name):

        body_part = next((x for x in self.parts if x.name == body_part_name), None)

        if body_part is None:
            raise ValueError('Body part '+str(body_part_name) +
                             ' does not belong to Agent '+str(self.name))

        return body_part

    def pre_step(self):
        """
        Reset actuators and reward to 0 before a new step of the environment.
        """

        # for part in self.parts:
        #     part.reset_actuators()

        self.reward = 0

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

        self.current_actions = actions_dict

        for actuator, value in actions_dict.items():

            for body_part in self.parts:
                body_part.apply_action(actuator, value)

    def reset(self):
        """
        Resets all body parts
        """
        self.position = self.initial_position
        self.velocity = [0,0,0]
        # for part in self.parts:
        #     part.reset()

    def draw(self, surface, excluded=None):
        """
        Draw the agent on the environment screen
        """

        if excluded is None:
            list_excluded = []
        else:
            list_excluded = excluded

        for part in self.parts:
            if part not in list_excluded:
                part.draw(surface, )

    def get_visual_sensor_shapes(self):

        shapes = []

        for sensor in self.sensors:

            if sensor.sensor_modality is SensorModality.VISUAL:
                if isinstance(sensor.shape, int):
                    shapes.append( [1, sensor.shape, 1])
                elif len(sensor.shape) == 2:
                    shapes.append([1, sensor.shape[0], 3])
                else:
                    shapes.append(sensor.shape)

        return shapes

