import pymunk, pygame

from flatland.agents.frames.frame import FrameGenerator, Frame

from flatland.utils.config import *

from pygame.locals import *

from flatland.default_parameters.agents import *


@FrameGenerator.register_subclass('forward')
class Forward(Frame):

    def __init__(self, agent_params):

        agent_params = {**forward_default, **agent_params}
        super(Forward, self).__init__(agent_params)

        self.longitudinal_velocity = 0
        self.angular_velocity = 0

    def apply_actions(self, action_commands):

        super().apply_actions(action_commands)

        self.longitudinal_velocity = self.actions.get('longitudinal_velocity', 0)
        vx = self.longitudinal_velocity*SIMULATION_STEPS
        vy = 0
        self.anatomy["base"].body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.base_translation_speed * (1.0 - SPACE_DAMPING) * 100, (0, 0))

        self.angular_velocity = self.actions.get('angular_velocity', 0)
        self.anatomy["base"].body.angular_velocity = self.angular_velocity * self.base_rotation_speed



    def get_movement_energy(self):

        energy = {}
        energy['base'] = abs(self.longitudinal_velocity) + abs(self.angular_velocity)

        return energy


    def get_default_key_mapping(self):

        mapping = super().get_default_key_mapping()

        mapping[K_LEFT] = ['press_hold', 'angular_velocity', 1]
        mapping[K_RIGHT] = ['press_hold', 'angular_velocity', -1]
        mapping[K_UP] = ['press_hold', 'longitudinal_velocity', 1]
        mapping[K_DOWN] = ['press_hold', 'longitudinal_velocity', -1]

        return mapping

    def get_available_actions(self):

        actions = super().get_available_actions()

        actions['longitudinal_velocity'] = [-1, 1, 'continuous']
        actions['angular_velocity'] = [-1, 1, 'continuous']

        return actions


