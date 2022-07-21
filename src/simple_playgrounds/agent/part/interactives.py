from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.agent.part.part import PhysicalPart
    from simple_playgrounds.entity.interactive import Graspable

import pymunk

from simple_playgrounds.agent.part.controller import BoolController, Controller
from simple_playgrounds.agent.part.part import InteractivePart
from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.entity.embodied import EmbodiedEntity


class Grasper(InteractivePart):
    def __init__(self, anchor: PhysicalPart, **kwargs):
        super().__init__(anchor, **kwargs)

        self.grasp_controller = self._controllers[0]

        self._grasped_entities = []
        self._grasping = False
        self._start_grasping = False
        self._grasp_joints = []

    @property
    def start_grasping(self):
        return self._start_grasping

    def grasp(self, entity: Graspable):

        if entity not in self._grasped_entities:
            self._grasped_entities.append(entity)
            entity.anchor.grasped_by.append(self)

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.GRASPER

    def _set_controllers(self, **kwargs) -> List[Controller]:
        grasper = BoolController(part=self)
        return [grasper]

    def apply_commands(self, **kwargs):
        command_value = self.grasp_controller.command_value

        if not command_value and self._grasping:
            self._release_grasping()

        elif self._start_grasping:

            for elem in self._grasped_entities:
                self._add_joints(elem)

            self._grasping = True
            self._start_grasping = False

        elif command_value and not self._grasping:
            self._start_grasping = True

    def _add_joints(self, entity: EmbodiedEntity):

        j_1 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 0), (0, 20))
        j_2 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 0), (0, -20))

        j_3 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 20), (0, 0))
        j_4 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, -20), (0, 0))

        grasp_joints = [j_1, j_2, j_3, j_4]
        self._grasp_joints += grasp_joints
        self._anchor.playground.space.add(*grasp_joints)

    def _release_grasping(self):

        for entity in self._grasped_entities:
            entity.anchor.grasped_by.remove(self)

        self._grasped_entities = []

        self._anchor.playground.space.remove(*self._grasp_joints)
        self._grasp_joints = []
        self._grasping = False
        self._start_grasping = False

    def reset(self):
        self._release_grasping()
        super().reset()
