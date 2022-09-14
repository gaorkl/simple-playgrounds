from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

import pymunk

from ...entity import EmbodiedEntity
from ...utils.definitions import CollisionTypes
from ..controller import BoolController
from ..device import Device

if TYPE_CHECKING:
    from ...entity import Graspable
    from ...utils.position import Coordinate
    from ..part import PhysicalPart


INTERACTOR_RADIUS = 5


class Interactor(Device):
    def __init__(self, anchor, **kwargs):

        super().__init__(anchor=anchor, **kwargs)

        # Point on the anchor
        self._anchor_coordinates = ((0, 0), 0)

    @property
    def anchor_coordinates(self):
        return self._anchor_coordinates

    @anchor_coordinates.setter
    def anchor_coordinates(self, coord: Coordinate):
        self._anchor_coordinates = coord

    def relative_position(self):

        return (self.position - self._anchor.position).rotated(-self._anchor.angle)

    def relative_angle(self):
        return self.angle - self._anchor.angle


class ActiveInteractor(Interactor):
    @abstractmethod
    def apply_commands(self, **kwargs):
        ...


class Grasper(ActiveInteractor):
    def __init__(self, anchor: PhysicalPart, **kwargs):
        super().__init__(anchor=anchor, **kwargs)

        self.grasp_controller = BoolController()

        self._grasped_entities = []
        self._grasping = False
        self._start_grasping = False
        self._grasp_joints = []

    @property
    def start_grasping(self):
        return self._start_grasping

    def grasp(self, graspable: Graspable):

        entity = graspable.anchor

        if entity not in self._grasped_entities:
            self._grasped_entities.append(entity)
            entity.grasped_by.append(self)

    @property
    def _collision_type(self):
        return CollisionTypes.GRASPER

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
            entity.grasped_by.remove(self)

        self._grasped_entities = []

        self._anchor.playground.space.remove(*self._grasp_joints)
        self._grasp_joints = []
        self._grasping = False
        self._start_grasping = False

    def reset(self):
        self._release_grasping()
        super().reset()
