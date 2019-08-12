import math
import pymunk, pygame

from ..entities.entity import Entity

from pygame.locals import *

from ..common import texture
from ..sensors import sensor




class PhysicalBody():

    def __init__(self):

        self.body = None
        self.shapes = None
        self.joint = None



class Agent(Entity):

    def __init__(self, agent_params):
        super(Agent, self).__init__()

        self.base_translation_speed = agent_params['base_translation_speed']
        self.base_rotation_speed = agent_params['base_rotation_speed']

        # Define the radius
        self.base_radius =  agent_params.get("base_radius")
        self.base_mass =  agent_params.get("base_mass")
        self.base_texture = agent_params['base_texture']

        self.health = agent_params.get('health')
        self.base_metabolism = agent_params.get('base_metabolism')
        self.action_metabolism = agent_params.get('action_metabolism')

        self.reward = 0

        # Base
        base = PhysicalBody()

        inertia = pymunk.moment_for_circle(self.base_mass, 0, self.base_radius, (0, 0))

        body = pymunk.Body(self.base_mass, inertia)

        #TODO: modify starting position. Make it potentially random, area, or multiple points.

        body.position = agent_params['starting_position'][:2]
        body.angle = agent_params['starting_position'][2]

        base.body = body

        shape = pymunk.Circle(body, self.base_radius, (0, 0))
        shape.elasticity = 0.1
        shape.collision_type = 1

        base.shape = shape

        self.is_activating = False

        self.anatomy = {"base" : base}

        self.texture = texture.Texture.create(self.base_texture)
        self.texture_surface = None

        self.sensors = {}
        self.observations = {}



    def add_sensor(self, sensor_param):

        sensor_param['minRange'] = self.base_radius + 2  # To avoid errors while logpolar converting
        new_sensor = sensor.SensorGenerator.create(self.anatomy, sensor_param)
        self.sensors[new_sensor.name] = new_sensor

    def compute_sensors(self, img):

        for sens in self.sensors:
            self.sensors[sens].update_sensor(img)

            self.observations[sens] = self.sensors[sens].observation

    def init_display(self):
        """
        Prepare a surface for displaying agent sensors, and measures
        :return:
        """
        pass

    def display_agent(self):
        """
        Update surface for agent
        :return:
        """



    def pre_step(self):

        self.reward = 0
        self.actions = []


    def draw(self,  surface):

        """
        Draw the agent on the environment screen
        """

        # TODO: refactor and simplifies. create texture in separate function, with init
        # Body
        radius = int(self.base_radius)

        # Create a texture surface with the right dimensions
        if self.texture_surface is None:
            self.texture_surface = self.texture.generate(radius * 2, radius * 2)
            self.mask =  pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            self.mask.fill((0, 0, 0, 0))
            pygame.draw.circle(self.mask, (255, 255, 255, 255), (radius, radius), radius)

            # Apply texture on mask
            self.mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
            pygame.draw.line(self.mask,  pygame.color.THECOLORS["blue"] , (radius,radius), (radius, 2*radius), 2)



        mask_rotated = pygame.transform.rotate(self.mask, self.anatomy['base'].body.angle * 180 / math.pi)
        mask_rect = mask_rotated.get_rect()
        mask_rect.center = self.anatomy['base'].body.position[1], self.anatomy['base'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask_rotated, mask_rect, None)


    def apply_action(self, actions):

        self.is_activating = bool(actions.get('activate', 0))
        self.is_eating = bool(actions.get('eat', 0))

        self.is_grasping = bool(actions.get('grasp', 0))
        self.is_releasing = bool(actions.get('release', 0))
        self.is_holding = False

        # Compute energy and reward
        if self.is_eating: self.reward -= self.action_metabolism
        if self.is_activating: self.reward -= self.action_metabolism

    def getStandardKeyMapping(self):
        mapping = {
            K_g: ['press_hold', 'grasp', 1],
            K_a: ['press_once', 'activate', 1],
            K_e: ['press_once', 'eat', 1]

        }

        return mapping

    def getAvailableActions(self):

        actions = {
            'grasp': [0, 1, 'discrete'],
            'activate': [0, 1, 'discrete'],
            'eat': [0, 1, 'discrete'],
        }

        return actions