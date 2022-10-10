from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Optional

import pymunk

from ...entity import EmbodiedEntity
from ...utils.definitions import CollisionTypes
from ..controller import GrasperController
from .interactor import ActiveInteractor

if TYPE_CHECKING:
    from ...entity import Graspable
    from ..part import PhysicalPart


class Grasper(ActiveInteractor, ABC):
    def __init__(
        self, anchor: PhysicalPart, max_grasped: Optional[int] = None, **kwargs
    ):
        super().__init__(anchor=anchor, **kwargs)

        self.grasp_controller = GrasperController("grasper")

        self._grasped_entities: List[EmbodiedEntity] = []

        self._grasp_joints: Dict[EmbodiedEntity, List[pymunk.PinJoint]] = {}

        self._can_grasp = False

        self._max_grasped = max_grasped

    @property
    def can_grasp(self):
        return self._can_grasp

    @property
    def grasped_entities(self):
        return self._grasped_entities

    def grasps(self, graspable: Graspable):

        assert self._can_grasp
        assert self._anchor

        entity = graspable.anchor

        if entity not in self._grasped_entities:

            if self._max_grasped and self._max_grasped <= len(self._grasped_entities):
                return

            self._grasped_entities.append(entity)
            self._add_joints(entity)
            entity.grasped_by.append(self)

            for sensor in self._anchor.agent.external_sensors:
                if sensor.invisible_grasped:
                    sensor.add_to_temporary_invisible(entity)

    @property
    def _collision_type(self):
        return CollisionTypes.GRASPER

    def _add_joints(self, entity: EmbodiedEntity):

        assert self._anchor

        j_1 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 0), (0, 20))
        j_2 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 0), (0, -20))

        j_3 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, 20), (0, 0))
        j_4 = pymunk.PinJoint(self._anchor.pm_body, entity.pm_body, (0, -20), (0, 0))

        grasp_joints = [j_1, j_2, j_3, j_4]
        self._grasp_joints[entity] = grasp_joints
        self._anchor.playground.space.add(*grasp_joints)

    def _release_grasping(self):

        for entity in list(self._grasped_entities):
            self.release(entity)

        self._can_grasp = False

        assert not self._grasped_entities
        assert not self._grasp_joints

    def release(self, entity):

        entity.grasped_by.remove(self)

        for sensor in self._anchor.agent.external_sensors:
            if sensor.invisible_grasped:
                sensor.remove_from_temporary_invisible(entity)

        joints = self._grasp_joints.pop(entity)
        self._anchor.playground.space.remove(*joints)

        self._grasped_entities.remove(entity)

    def reset(self):
        self._release_grasping()
        super().reset()


class GraspHold(Grasper):
    def __init__(self, anchor, **kwargs):

        super().__init__(anchor, **kwargs)

        self._is_grasping = False

    def apply_commands(self, **kwargs):
        command_value = self.grasp_controller.command_value

        if not command_value:
            self._release_grasping()
            self._is_grasping = False
        else:
            if not self._is_grasping:
                self._can_grasp = True
                self._is_grasping = True

            else:
                self._can_grasp = False


class GraspMagnet(Grasper):
    def apply_commands(self, **kwargs):
        command_value = self.grasp_controller.command_value

        if not command_value:
            self._release_grasping()
        else:
            self._can_grasp = True
