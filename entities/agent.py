import pymunk, pygame, math

from .entity import  Entity
from utils.config import *
from utils import pygame_utils


class BasicAgent(Entity):

    def __init__(self, agent_params, space):
        super(BasicAgent, self).__init__()

        self.x, self.y, self.theta
        self.speed = agent_params['speed']
        self.rotation_speed = agent_params['rotation_speed']

        # Define the radius
        self.radius = 10
        self.agent_mass = 10
        self.color = agent_params['color']

        self.health = agent_params.get('health', 1000)
        self.reward = 0
        self.base_metabolism = agent_params.get('base_metabolism', 0)
        self.action_metabolism = agent_params.get('action_metabolism', 0)

        # Create the body
        #
        # b = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        #
        # self.shape = pymunk.Circle(
        #     body=b,
        #     radius=self.radius
        # )

        # self.x, self.y, self.theta = agent_params['position']
        #


        AGENT_ELASTICITY = 0.1
        #
        # # Create the body
        # inertia = pymunk.moment_for_circle(10, 0, self.radius, (0, 0))
        # body = pymunk.Body(50, inertia)
        # c_shape = pymunk.Circle(body, self.radius)
        # c_shape.elasticity = 1.0
        # body.position = self.x, self.y
        # c_shape.collision_type = 0
        # body.angle = self.theta
        # #body.entity = self
        #
        # space.add(body, c_shape)

        inertia = pymunk.moment_for_circle(self.agent_mass, 0, self.radius, (0, 0))

        body = pymunk.Body(self.agent_mass, inertia)
        body.position = agent_params['position'][:2]
        body.angle = agent_params['position'][2]

        self.shape = pymunk.Circle(body, self.radius, (0, 0))
        self.shape.elasticity = AGENT_ELASTICITY
        self.shape.collision_type = 1

        space.add(body, self.shape)

        self.body = body


        self.texture = pygame.Surface((2*self.radius, 2*self.radius))
        self.texture.fill(self.color)
        self.texture.set_colorkey((0, 0, 0, 0))

        self.is_activating = False


    def pre_step(self):

        self.reward = 0
        self.actions = []

    def apply_action(self, actions):
        longitudinal_velocity = actions.get('longitudinal_velocity', 0)
        lateral_velocity = actions.get('lateral_velocity', 0)
        angular_velocity = actions.get('angular_velocity', 0)

        #vx = longitudinal_velocity * math.cos(self.theta) + lateral_velocity * math.cos(self.theta + 0.5 * math.pi)

        #vy = longitudinal_velocity * math.sin(self.theta) + lateral_velocity * math.sin(self.theta + 0.5 * math.pi)
        #self.body.velocity = self.speed * pymunk.Vec2d(vx, vy)

        vx = longitudinal_velocity*SIMULATION_STEPS/10.0
        vy = lateral_velocity*SIMULATION_STEPS/10.0
        self.body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.speed * (1.0 - SPACE_DAMPING) * 100, (0, 0))

        #coeff =  self.agent_mass / 10.0
        #print(self.body.velocity[1], self.speed, self.body.moment, self.radius, self.agent_mass)

        self.body.angular_velocity = angular_velocity * self.rotation_speed

        self.is_activating = bool(actions.get('activate', 0))
        self.is_eating = bool(actions.get('eat', 0))

        self.is_grasping = bool(actions.get('grasp', 0))
        self.is_releasing = bool(actions.get('release', 0))
        self.is_holding = False



        # Compute energy and reward
        if self.is_eating: self.reward -= self.action_metabolism
        if self.is_activating: self.reward -= self.action_metabolism

        self.reward -= self.base_metabolism*(abs(longitudinal_velocity) + abs(lateral_velocity) + abs(angular_velocity))
        self.health += self.reward



    def draw(self, surface):
        """
        Draw the agent on the environment screen
        """

        # # Create the mask
        # mask = pygame.Surface((self.radius * 2, self.radius * 2))
        # mask.fill((0, 0, 0, 0))
        # pygame.draw.circle(mask, (255, 255, 255, 255), (self.radius, self.radius), self.radius)
        #
        # # Apply texture on mask
        # mask.blit(self.texture, (0, 0), None, pygame.BLEND_MULT)
        # mask_rect = mask.get_rect()
        # mask_rect.center = pygame_utils.to_pygame((self.x, self.y), surface)
        #
        # # Blit the masked texture on the screen
        # surface.blit(mask, mask_rect, None)
        #
        # circle_center = (self.x, self.y)
        # p = pygame_utils.to_pygame(circle_center, surface)
        #
        # circle_edge = circle_center + pymunk.Vec2d(self.radius, 0).rotated(self.theta)
        # p2 = pygame_utils.to_pygame(circle_edge, surface)
        # line_r = 3
        # pygame.draw.lines(surface, pygame.color.THECOLORS["blue"], False, [p, p2], line_r)


