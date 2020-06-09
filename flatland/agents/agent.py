from .sensors import sensor
from .sensors.visual_sensors.visual_sensor import VisualSensor
from .sensors.geometric_sensors.geometric_sensor import GeometricSensor
from .body_parts.parts import BodyBase

from .controllers.collection.human import Keyboard
import os, yaml
import math

# __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# with open(os.path.join(__location__, 'agent_default.yml'), 'r') as yaml_file:
#     default_config = yaml.load(yaml_file)


class Agent():
    """
    Base class for agents

    """
    index_name = 0
    body_parts_visible = False

    def __init__(self, initial_position, base, **agent_param):

        if 'name' in agent_param:
            self.name =  agent_param.get('name')
        else:
            self.name = 'agent_' + str(type(self).index_name)
            type(self).index_name += 1

        # self.health = agent_metabolism_params.get('health')
        # self.base_metabolism = agent_metabolism_params.get('base_metabolism')
        # self.action_metabolism = agent_metabolism_params.get('action_metabolism')

        # # Frame
        # self.frame = frame.FrameGenerator.create(self.agent_type, custom_config.get('frame', {}))
        # self.available_actions = self.frame.get_available_actions()

        # Select Controller
        # self.controller = controller.ControllerGenerator.create(controller_type)
        # self.controller.set_available_actions(self.available_actions)


        # Dictionary for sensors
        self.sensors = {}

        # Body parts
        self.base = base
        self.body_parts = [self.base]

        # Possible actions
        self.available_actions = {}

        # Internals
        # self.is_activating = False
        # self.is_eating = False
        #
        # self.is_grasping = False
        # self.grasped = []
        # self.is_holding = False

        self.reward = 0
        self.energy_spent = 0

        # Default starting position
        self.initial_position = initial_position

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False

        # Replaced when agent is put in playground
        self.size_playground = [0, 0]

        self.actions_mapping = {}


    def assign_controller(self, controller):
        # Controller
        self.controller = controller
        self.controller.set_available_actions(self.get_actions())


    @staticmethod
    def parse_configuration(entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]

    @property
    def initial_position(self):
        # differentiate between case where initial position is fixed and case where it is random
        if isinstance( self._initial_position, list ) or isinstance( self._initial_position, tuple ) :
            return self._initial_position
        else:
            return self._initial_position.sample()

    @initial_position.setter
    def initial_position(self, position):
        self._initial_position = position


    #Todo: check if this can be replaced by a 'pointer'

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
        self.base.velocity = velocity

    @property
    def size_playground(self):
        return self.size_playground

    @size_playground.setter
    def size_playground(self, size_pg):
        self._size_playground = size_pg
        for part in self.body_parts:
            part.size_playground = size_pg

    def pick_actions(self):

        # if isinstance(self.controller, Keyboard):

        actions = self.controller.get_actions()

        return actions

    def owns_shape(self, pm_shape):

        all_shapes = [part.pm_visible_shape for part in self.body_parts]
        if pm_shape in all_shapes:
            return True
        return False

    def add_sensor(self, sensor_type, sensor_name, sensor_config = None, **sensor_params):

        if sensor_type is 'touch':
            sensor_params['minRange'] = self.base.radius   # To avoid errors while linearpolar converting

        if sensor_config == None:
            sensor_config = {}

            sensor_params = {**sensor_config, **sensor_params}

        sensor_params['name'] = sensor_name
        sensor_params['type'] = sensor_type


        new_sensor = sensor.SensorGenerator.create(sensor_type, self.frame.anatomy, sensor_params)

        if new_sensor.sensor_modality == sensor.SensorModality.GEOMETRIC:
             self.has_geometric_sensor = True
        if new_sensor.sensor_modality == sensor.SensorModality.VISUAL:
            self.has_visual_sensor = True
        self.sensors[sensor_name] = new_sensor

    def compute_sensors(self, img, entities, agents):

        for sensor_name in self.sensors:

            if self.sensors[sensor_name].sensor_modality == sensor.SensorModality.GEOMETRIC:
                self.sensors[sensor_name].update_sensor(self, entities, agents)

            elif self.sensors[sensor_name].sensor_modality == sensor.SensorModality.VISUAL:
                self.sensors[sensor_name].update_sensor(img)

            else:
                raise "Sensor calculation modality is not specified for "+sensor_name

    def pre_step(self):

        self.reward = 0
        self.energy_spent = 0

    def add_body_part(self, part):


        self.body_parts.append(part)


    def add_joint(self, part_1, part_2, type_joint):

        pass

    def get_actions(self):

        actions = []

        for part in self.body_parts:

            actions = actions + part.get_available_actions()

        return actions

    def find_part_by_name(self, body_part_name):

        body_part = next((x for x in self.body_parts if x.name == body_part_name), None)

        if body_part is None:
            raise ValueError('Body part '+str(body_part_name)+' does not belong to Agent '+str(self.name))

        return body_part

    def apply_action_to_physical_body(self, actions_dict):

        for body_part_name, actions in actions_dict.items():

            body_part = self.find_part_by_name(body_part_name)
            body_part.apply_actions(actions)



        #
        #
        #
        # self.action_commands = actions
        #
        #
        # self.is_activating = bool(self.action_commands.get('activate', 0))
        # self.is_eating = bool(self.action_commands.get('eat', 0))
        # self.is_grasping = bool(self.action_commands.get('grasp', 0))
        #
        # if self.is_holding and not self.is_grasping:
        #     self.is_holding = False
        #
        # # Compute energy and reward
        # if self.is_eating: self.energy_spent += self.action_metabolism
        # if self.is_activating: self.energy_spent += self.action_metabolism
        # if self.is_holding: self.energy_spent += self.action_metabolism
        #
        # self.frame.apply_actions(self.action_commands)
        #
        # movement_energy = self.frame.get_movement_energy()
        # self.energy_spent += self.base_metabolism * sum( energy for part, energy in movement_energy.items() )


    def reset(self):

        for part in self.body_parts:
            if part.can_activate:
                part.is_activating = False
            if part.can_eat:
                part.is_eating = False
            if part.can_grasp:
                part.is_grasping = False
                part.grasped = []
                part.is_holding = False

    def draw(self, surface, visible_to_self=False):
        """
        Draw the agent on the environment screen
        """

        for part in self.body_parts:

            if not visible_to_self:

                part.draw(surface)


# class ForwardAgent(Agent):
#
#     def __init__(self, initial_position, controller_type, **kwargs):
#
#         default_config = self.parse_configuration('agent', 'forward')
#         agent_params = {**default_config, **kwargs}
#
#         base_params = agent_params['base']
#
#         base = BodyBase(initial_position, controller_type, **base_params)
#         self.add_body_part(base)

