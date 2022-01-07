from typing import Optional, TYPE_CHECKING

import pymunk

from simple_playgrounds.entity.embodied.interactive import StandAloneInteractive, AnchoredInteractive
from simple_playgrounds.common.definitions import CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.entity.embodied.appearance.texture import ColorTexture
from simple_playgrounds.agent.agent import Agent


class MockAgent(Agent):

    def __init__(self, **kwargs):
        super().__init__(
            appearance=ColorTexture(color=(121, 10, 220)), 
            shape='circle',
            radius=4,
            movable=True,
            mass=10,
            **kwargs)

    def post_step(self):
        pass

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.PART


