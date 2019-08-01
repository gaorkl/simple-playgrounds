import pymunk, pygame

from .agent import Agent

from ..utils.config import *

from pygame.locals import *

class ForwardAgent(Agent):

    def __init__(self, agent_params):

        super(ForwardAgent, self).__init__(agent_params)

    def apply_action(self, actions):
        super().apply_action(actions)

        longitudinal_velocity = actions.get('longitudinal_velocity', 0)
        angular_velocity = actions.get('angular_velocity', 0)

        vx = longitudinal_velocity*SIMULATION_STEPS/10.0
        vy = 0
        self.anatomy["base"].body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.speed * (1.0 - SPACE_DAMPING) * 100, (0, 0))

        self.anatomy["base"].body.angular_velocity = angular_velocity * self.rotation_speed


        self.reward -= self.base_metabolism*(abs(longitudinal_velocity) + abs(angular_velocity))
        self.health += self.reward

    def getStandardKeyMapping(self):

        mapping = super().getStandardKeyMapping()

        mapping[K_LEFT] = ['press_hold', 'angular_velocity', 1]
        mapping[K_RIGHT] = ['press_hold', 'angular_velocity', -1]
        mapping[K_UP] = ['press_hold', 'longitudinal_velocity', 1]

        return mapping

    def getAvailableActions(self):

        actions = super().getAvailableActions()

        actions['longitudinal_velocity'] = [0, 1, 'continuous']
        actions['angular_velocity'] = [-1, 1, 'continuous']

        return actions

    def draw(self, surface):
        pass