from ..utils.definitions import SensorModality
from flatland.utils.position_utils import PositionAreaSampler


class Agent:
    """
    Base class for agents

    """
    index_agent = 0

    def __init__(self, initial_position, base, **agent_params):
        """
        Base class for agents. Need a base object (BodyBase)

        Args:
            initial_position: initial position of the base
            base: BodyBase object, required to initialize an agent (all agents have a base)
            **agent_param: other parameters
        """

        self.name = agent_params.get('name', None)

        if self.name is None:
            self.name = 'agent_' + str(Agent.index_agent)
        Agent.index_agent += 1

        # Dictionary for sensors
        self.sensors = []

        # Body parts
        self.base = base
        self.body_parts = [self.base]

        # Possible actions
        self.available_actions = {}

        self.reward = 0
        self.energy_spent = 0

        # Default starting position
        self.initial_position = initial_position

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False

        # Replaced when agent is put in playground
        self.size_playground = [0, 0]

        # Controller should be replaced
        self.controller = None

    @property
    def key_mapping(self):
        return None

    @property
    def initial_position(self):
        # differentiate between case where initial position is fixed and case where it is random
        if isinstance(self._initial_position, list) or isinstance(self._initial_position, tuple):
            return self._initial_position
        elif isinstance(self._initial_position, PositionAreaSampler):
            return self._initial_position.sample()
        else:
            return self._initial_position

    @initial_position.setter
    def initial_position(self, position):
        self._initial_position = position

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, position):

        for part in self.body_parts:

            if part is self.base:
                part.position = position

            else:
                part.set_relative_position()

    @property
    def velocity(self):
        return self.base.velocity

    @velocity.setter
    def velocity(self, velocity):
        for part in self.base:
            part.velocity = velocity

    @property
    def size_playground(self):
        return self.size_playground

    @size_playground.setter
    def size_playground(self, size_pg):
        self._size_playground = size_pg
        for part in self.body_parts:
            part.size_playground = size_pg

    def add_sensor(self, new_sensor):

        if new_sensor.sensor_modality == SensorModality.GEOMETRIC:
            self.has_geometric_sensor = True
        elif new_sensor.sensor_modality == SensorModality.VISUAL:
            self.has_visual_sensor = True

        self.sensors.append(new_sensor)

    def add_body_part(self, part):

        part.part_number = len(self.body_parts)
        self.body_parts.append(part)

    def get_bodypart_from_shape(self, pm_shape):
        return next(iter([part for part in self.body_parts if part.pm_visible_shape == pm_shape]), None)

    def assign_controller(self, controller):
        # Controller
        self.controller = controller
        # self.controller.set_available_actions(self.get_all_available_actions())
        #
        # if self.controller.require_key_mapping:
        #     self.controller.assign_key_mapping(self.key_mapping)

    def owns_shape(self, pm_shape):

        all_shapes = [part.pm_visible_shape for part in self.body_parts]
        if pm_shape in all_shapes:
            return True
        return False

    def find_part_by_name(self, body_part_name):

        body_part = next((x for x in self.body_parts if x.name == body_part_name), None)

        if body_part is None:
            raise ValueError('Body part '+str(body_part_name)+' does not belong to Agent '+str(self.name))

        return body_part

    def pre_step(self):

        self.reward = 0
        self.energy_spent = 0

    def get_all_available_actions(self):

        actions = []
        for part in self.body_parts:
            actions = actions + part.get_available_actions()

        return actions

    def apply_actions_to_body_parts(self, actions_dict):

        for body_part_name, actions in actions_dict.items():

            body_part = self.find_part_by_name(body_part_name)
            body_part.apply_actions(actions)

    def reset(self):

        for part in self.body_parts:
            part.reset()

    def draw(self, surface, excluded=None):
        """
        Draw the agent on the environment screen
        """

        if excluded is None:
            list_excluded = []
        else:
            list_excluded = excluded

        for part in self.body_parts:
            if part not in list_excluded:
                part.draw(surface)
