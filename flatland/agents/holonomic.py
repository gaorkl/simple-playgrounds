import pymunk, pygame

from .forward import ForwardAgent

from ..utils.config import *

from pygame.locals import *

class HolonomicAgent(ForwardAgent):

    def __init__(self, agent_params):

        super(HolonomicAgent, self).__init__(agent_params)

    def apply_action(self, actions):
        super().apply_action(actions)

        longitudinal_velocity = actions.get('longitudinal_velocity', 0)
        vx = longitudinal_velocity * SIMULATION_STEPS / 10.0

        lateral_velocity = actions.get('lateral_velocity', 0)
        vy = lateral_velocity * SIMULATION_STEPS / 10.0

        self.anatomy["base"].body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.speed * (1.0 - SPACE_DAMPING) * 100, (0, 0))

        self.reward -= self.base_metabolism * (abs(lateral_velocity) )

    def getStandardKeyMapping(self):

        mapping = super().getStandardKeyMapping()

        mapping[K_LEFT] = ['press_hold', 'lateral_velocity', 1]
        mapping[K_RIGHT] = ['press_hold', 'lateral_velocity', -1]

        mapping[K_z] = ['press_hold', 'angular_velocity', 1]
        mapping[K_x] = ['press_hold', 'angular_velocity', -1]

        return mapping

    def getAvailableActions(self):
        actions = super().getAvailableActions()

        actions['lateral_velocity'] = [-1, 1, 'continuous']

        return actions

    def draw(self, surface):
        pass