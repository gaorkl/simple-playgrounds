from .sensors import sensor
from .geometric_sensors import geometric_sensor
from .frames import frame
from .controllers import controller

import os, yaml
import math

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'agent_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)

class Agent():

    index_name = 0

    def __init__(self, agent_type , controller_type = 'keyboard', **custom_config):
        super(Agent, self).__init__()


        self.agent_type = agent_type
        if 'name' in custom_config:
            self.name =  custom_config.get('name')
        else:
            self.name = 'agent_' + str(type(self).index_name)
            type(self).index_name += 1

        # Metabolism
        if custom_config is None:
            custom_config = {}

        agent_metabolism_params = {**default_config['metabolism'], **custom_config.get('metabolism', {}) }
        self.health = agent_metabolism_params.get('health')
        self.base_metabolism = agent_metabolism_params.get('base_metabolism')
        self.action_metabolism = agent_metabolism_params.get('action_metabolism')

        # Frame
        self.frame = frame.FrameGenerator.create(self.agent_type, custom_config.get('frame', {}))
        self.available_actions = self.frame.get_available_actions()

        # Select Controller
        self.controller = controller.ControllerGenerator.create(controller_type)
        self.controller.set_available_actions(self.available_actions)

        if self.controller.require_key_mapping:
            default_key_mapping = self.frame.get_default_key_mapping()
            self.controller.assign_key_mapping(default_key_mapping)

        # Dictionary for sensors
        self.sensors = {}

        # Internals
        self.is_activating = False
        self.is_eating = False
        self.is_grasping = False
        self.grasped = []
        self.is_holding = False
        self.reward = 0
        self.energy_spent = 0

        self.observations = {}
        self.action_commands = {}


        # Default starting position
        self.initial_position = custom_config.get('position', None)

        # Information about sensor types
        self.has_geometric_sensor = False
        self.has_visual_sensor = False


    def get_initial_position(self):

        # differentiate between case where initial position is fixed and case where it is random

        if isinstance( self.initial_position, list ) or isinstance( self.initial_position, tuple ) :

            return self.initial_position

        else:

            return self.initial_position.sample()


    @property
    def position(self):

        x,y = self.frame.anatomy['base'].body.position
        phi = self.frame.anatomy['base'].body.angle

        coord_x = self.size_playground[0] - y
        coord_y = x
        coord_phi = (phi + math.pi/2) % (2*math.pi)

        return coord_x, coord_y, coord_phi

    @position.setter
    def position(self, position):
        coord_x, coord_y, coord_phi = position

        y = self.size_playground[0] - coord_x
        x = coord_y
        phi = coord_phi - math.pi / 2


        for part_name, part in self.frame.anatomy.items():

            if part.body is not None:

                part.body.position = [ x + part.body.position[0], y + part.body.position[1]]
                part.body.angle = phi + part.body.angle


        #self.frame.anatomy['base'].body.position = x, y
        #self.frame.anatomy['base'].body.angle = phi

    @property
    def velocity(self):
        vx, vy = self.frame.anatomy['base'].body.velocity
        vphi = self.frame.anatomy['base'].body.angular_velocity

        vx, vy = -vy, vx
        return vx, vy, vphi

    @velocity.setter
    def velocity(self, velocity):
        vx, vy, vphi = velocity

        for part_name, part in self.frame.anatomy.items():

            if part.body is not None:
                part.body.velocity = (vx, vy)
                part.body.angular_velocity = vphi




    def owns_shape(self, pm_shape):

        all_shapes = []
        for part_name, part in self.frame.anatomy.items():
            all_shapes += [part.shape]

        if pm_shape in all_shapes:
            return True

        else:
            return False

    def add_sensor(self, sensor_type, sensor_name, sensor_config = None, **sensor_params):

        if sensor_type is 'touch':
            sensor_params['minRange'] = self.frame.base_radius   # To avoid errors while logpolar converting

        if sensor_config == None:
            sensor_config = {}

            sensor_params = {**sensor_config, **sensor_params}

        sensor_params['name'] = sensor_name
        sensor_params['type'] = sensor_type


        #Brait
        if sensor_type is 'lidar':
            new_sensor = geometric_sensor.LidarSensor(self.frame.anatomy, sensor_params)
            self.has_geometric_sensor = True
        else:
            new_sensor = sensor.SensorGenerator.create(sensor_type, self.frame.anatomy, sensor_params)
            self.has_visual_sensor = True
        self.sensors[sensor_name] = new_sensor

    #Brait
    #Pas donner que l'image
    def compute_sensors(self, img, current_agent, entities, agents):

        for sensor_name in self.sensors:

            if self.sensors[sensor_name].sensor_type == "lidar":
                self.sensors[sensor_name].update_sensor(current_agent, entities, agents)
            else:
                self.sensors[sensor_name].update_sensor(img)

            self.observations[sensor_name] = self.sensors[sensor_name].observation

    def pre_step(self):

        self.reward = 0
        self.energy_spent = 0

    def get_controller_actions(self):

        return self.controller.get_actions()

    def apply_action_to_physical_body(self, actions):

        self.action_commands = actions


        self.is_activating = bool(self.action_commands.get('activate', 0))
        self.is_eating = bool(self.action_commands.get('eat', 0))
        self.is_grasping = bool(self.action_commands.get('grasp', 0))

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

        # Compute energy and reward
        if self.is_eating: self.energy_spent += self.action_metabolism
        if self.is_activating: self.energy_spent += self.action_metabolism
        if self.is_holding: self.energy_spent += self.action_metabolism

        self.frame.apply_actions(self.action_commands)

        movement_energy = self.frame.get_movement_energy()
        self.energy_spent += self.base_metabolism * sum( energy for part, energy in movement_energy.items() )


    def reset(self):

        self.is_activating = False
        self.is_eating = False
        self.is_grasping = False
        self.grasped = []
        self.is_holding = False
