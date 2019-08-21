import pymunk, pygame

from flatland.agents.physical_bodies.physical_body import BodyGenerator, PhysicalBody

from flatland.utils.config import *

from pygame.locals import *

from flatland.default_parameters.agents import *

@BodyGenerator.register_subclass('forward')
class Forward(PhysicalBody):

    def __init__(self, agent_params):

        agent_params = {**forward_default, **agent_params}
        super(Forward, self).__init__(agent_params)

        self.longitudinal_velocity = 0
        self.angular_velocity = 0

    def apply_action(self, actions):

        self.longitudinal_velocity = actions.get('longitudinal_velocity', 0)
        vx = longitudinal_velocity*SIMULATION_STEPS/10.0
        vy = 0
        self.anatomy["base"].body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.base_translation_speed * (1.0 - SPACE_DAMPING) * 100, (0, 0))

        angular_velocity = actions.get('angular_velocity', 0)
        self.anatomy["base"].body.angular_velocity = angular_velocity * self.base_rotation_speed

    def energy_spent(self):

        energy = {}
        energy['base'] = longitudinal_velocity +

    def getStandardKeyMapping(self):

        mapping = {}

        mapping[K_LEFT] = ['press_hold', 'angular_velocity', 1]
        mapping[K_RIGHT] = ['press_hold', 'angular_velocity', -1]
        mapping[K_UP] = ['press_hold', 'longitudinal_velocity', 1]

        return mapping

    def getAvailableActions(self):

        actions = {}

        actions['longitudinal_velocity'] = [0, 1, 'continuous']
        actions['angular_velocity'] = [-1, 1, 'continuous']

        return actions


