from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

import pymunk
from gymnasium.spaces import Discrete

from spg.core.entity.action import ActionMixin

if TYPE_CHECKING:
    from spg.core.playground import Playground


class GraspableMixin:

    pm_body: pymunk.Body
    pm_shapes: List[pymunk.Shape]

    grasped_by = []


class GrasperMixin(ActionMixin):

    pm_shapes: List[pymunk.Shape]
    pm_body: pymunk.Body
    playground: Playground

    grasped: Dict[GraspableMixin, List[pymunk.PinJoint]] = {}
    max_grasped: int = None

    @property
    def action_space(self):
        return Discrete(2)

    def grasp(self):

        shapes_in_range = []

        for shape in self.pm_shapes:
            shapes_in_range.extend(
                (sq.shape for sq in self.playground.space.shape_query(shape))
            )

        entities_in_range = set(
            [
                self.playground.shapes_to_entities[shape]
                for shape in set(shapes_in_range)
            ]
        )

        graspables_in_range = [
            entity for entity in entities_in_range if isinstance(entity, GraspableMixin)
        ]

        for graspable in graspables_in_range:
            if graspable not in self.grasped:
                self.grasp_entity(graspable)

    def grasp_entity(self, entity: GraspableMixin):

        assert entity not in self.grasped

        if self.max_grasped is not None and len(self.grasped) >= self.max_grasped:
            return

        # If grasper has no body, use body of anchor
        pm_body = self.pm_body
        if not pm_body:
            pm_body = self.anchor.pm_body

        j_1 = pymunk.PinJoint(pm_body, entity.pm_body, (0, 0), (0, 20))
        j_2 = pymunk.PinJoint(pm_body, entity.pm_body, (0, 0), (0, -20))

        j_3 = pymunk.PinJoint(pm_body, entity.pm_body, (0, 20), (0, 0))
        j_4 = pymunk.PinJoint(pm_body, entity.pm_body, (0, -20), (0, 0))

        grasp_joints = [j_1, j_2, j_3, j_4]
        self.grasped[entity] = grasp_joints

        entity.grasped_by.append(self)
        self.playground.space.add(*grasp_joints)

    def release_all(self):
        for entity in self.grasped.copy():
            self.release_entity(entity)

    def release_entity(self, entity):
        joints = self.grasped.pop(entity)
        self.playground.space.remove(*joints)
        entity.grasped_by.remove(self)


class GrasperHold(GrasperMixin):

    is_grasping = False

    def apply_action(self, action):

        if not action:
            self.release_all()
            self.is_grasping = False
        else:
            if not self.is_grasping:
                self.is_grasping = True
                self.grasp()


class GrasperMagnet(GrasperMixin):
    def apply_action(self, action):

        if not action:
            self.release_all()
        else:
            self.grasp()
