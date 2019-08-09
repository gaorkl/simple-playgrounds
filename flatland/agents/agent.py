import math
import pymunk, pygame

from ..entities.entity import Entity

from pygame.locals import *

from ..common import texture
from ..sensors import sensor


default_texture =  {
        'type': 'color',
        'color': (217, 35, 144)
    }



class PhysicalBody():

    def __init__(self):

        self.body = None
        self.shapes = None
        self.joint = None



class Agent(Entity):

    def __init__(self, agent_params):
        super(Agent, self).__init__()

        self.speed = agent_params['speed']
        self.rotation_speed = agent_params['rotation_speed']

        # Define the radius
        self.radius =  agent_params.get("radius", 20)
        self.agent_mass =  agent_params.get("mass", 10)
        self.color = agent_params['color']

        self.health = agent_params.get('health', 1000)
        self.reward = 0
        self.base_metabolism = agent_params.get('base_metabolism', 0)
        self.action_metabolism = agent_params.get('action_metabolism', 0)

        AGENT_ELASTICITY = 0.1


        # Base

        base = PhysicalBody()

        inertia = pymunk.moment_for_circle(self.agent_mass, 0, self.radius, (0, 0))

        body = pymunk.Body(self.agent_mass, inertia)
        body.position = agent_params['position'][:2]
        body.angle = agent_params['position'][2]

        base.body = body

        shape = pymunk.Circle(body, self.radius, (0, 0))
        shape.elasticity = AGENT_ELASTICITY
        shape.collision_type = 1

        base.shape = shape

        self.is_activating = False

        self.anatomy = {"base" : base}

        text = agent_params.get('texture', default_texture)
        self.texture = texture.Texture.create(text)
        self.texture_surface = None

        self.sensors = {}
        self.observations = {}



    def add_sensor(self, sensor_param):

        sensor_param['minRange'] = self.radius + 2  # To avoid errors while converting
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

        # Body
        radius = int(self.radius)

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