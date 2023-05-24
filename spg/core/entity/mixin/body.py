from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Union

import arcade
import pymunk

from spg.core.position import Coordinate, CoordinateSampler

if TYPE_CHECKING:
    from ...playground import Playground
    from ..entity import Entity


class BodyMixin(ABC):

    sprite: arcade.Sprite
    playground: Playground
    attached: List[AttachmentMixin]

    def __init__(self, mass: Optional[float] = None, **_):

        self.mass = mass
        self.movable = bool(mass)

        self.pm_body = self._get_pm_body()
        self._moved = False

    @abstractmethod
    def _get_pm_body(self) -> pymunk.Body:
        ...

    @property
    def coordinates(self):
        return self.position, self.angle

    @property
    def position(self):
        """Position (x, y)"""
        return self.pm_body.position

    @property
    def angle(self):
        """Absolute orientation"""
        return self.pm_body.angle % (2 * math.pi)

    @property
    def velocity(self):
        return self.pm_body.velocity

    @property
    def angular_velocity(self):
        return self.pm_body.angular_velocity

    @property
    def moved(self):

        if self._moved:
            return True

        if self.pm_body.body_type == pymunk.Body.DYNAMIC:

            vel = self.pm_body.velocity.length
            if vel > 0.001:
                return True

            ang_vel = self.pm_body.angular_velocity
            if abs(ang_vel) > 0.001:
                return True

        return False

    @property
    def base(self):
        return self


class BaseMixin(BodyMixin):
    def move_to(
        self,
        coordinates: Union[Coordinate, CoordinateSampler],
        allow_overlapping: bool = True,
    ):

        if isinstance(coordinates, CoordinateSampler):
            if allow_overlapping:
                coordinates = coordinates.sample()
            else:
                coordinates = coordinates.sample_non_overlapping(self)

        elif not allow_overlapping:
            if self.playground.check_overlapping(self, coordinates):
                raise ValueError("Entity overlaps with another entity")

        # Apply new position and velocities
        self.pm_body.position, self.pm_body.angle = coordinates
        self.pm_body.velocity, self.pm_body.angular_velocity = (0, 0), 0

        if self.pm_body.space:
            self.pm_body.space.reindex_shapes_for_body(self.pm_body)

        self._moved = True

        for attached_entity in self.attached:
            attached_entity.move_relative()

        if self.pm_body.space:
            self.pm_body.space.reindex_shapes_for_body(self.pm_body)

    def fix_attached(self):
        for attachment in self.attached:
            attachment.fix()


class BaseStaticMixin(BaseMixin):
    def _get_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)


class BaseDynamicMixin(BaseMixin):
    def _get_pm_body(self):

        vertices = self.sprite.get_hit_box()
        moment = pymunk.moment_for_poly(self.mass, vertices)
        return pymunk.Body(self.mass, moment, body_type=pymunk.Body.DYNAMIC)


class AttachmentMixin(BodyMixin):

    anchor: Optional[Entity]

    def __init__(self, attachment_point, **kwargs):
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def attachment_point(self):
        ...

    @property
    def initial_relative_coordinate(self):

        anchor_attachment_point, relative_angle = self.anchor.attachment_points[self]
        anchor_attachment_point = pymunk.Vec2d(*anchor_attachment_point)

        entity_relative_position = anchor_attachment_point - pymunk.Vec2d(
            *self.attachment_point
        ).rotated(relative_angle)

        return entity_relative_position, relative_angle

    def move_relative(self):

        assert self.anchor

        self._move_relative()

        for attached_entity in self.attached:
            attached_entity.move_relative()

        self._moved = True

    @abstractmethod
    def _move_relative(self):
        ...

    @property
    def base(self):
        return self.anchor.base

    def fix(self):

        self._fix()

        for attachment in self.attached:
            attachment.fix()

    @abstractmethod
    def _fix(self):
        ...


class AttachedStaticMixin(AttachmentMixin):

    pm_shapes: List[pymunk.Shape]
    attached: list[AttachmentMixin]

    def _get_pm_body(self):
        return None

    def _move_relative(self):
        pass

    def _fix(self):
        pass

    @property
    def position(self):

        position_entity = self.anchor.position + self.initial_relative_coordinate[
            0
        ].rotated(self.anchor.angle + self.initial_relative_coordinate[1])
        return position_entity

    @property
    def angle(self):
        return self.anchor.angle + self.initial_relative_coordinate[1]


class AttachedDynamicMixin(AttachmentMixin):

    attached: list[AttachmentMixin]
    anchor: Entity
    pm_body: pymunk.Body
    pm_shapes: list[pymunk.Shape]
    _joint: Optional[pymunk.Constraint]
    _limit: Optional[pymunk.Constraint]
    _motor: Optional[pymunk.Constraint]
    playground: Playground

    def _fix(self):
        self.joint = self._get_joint()
        self.limit = self._get_limit()
        self.motor = self._get_motor()

        if self.joint is not None:
            self.playground.space.add(self.joint)

        if self.limit is not None:
            self.playground.space.add(self.limit)

        if self.motor is not None:
            self.playground.space.add(self.motor)

    def _move_relative(self):
        position_anchor = pymunk.Vec2d(*self.anchor.position)
        angle_anchor = self.anchor.pm_body.angle

        position_entity = position_anchor + self.initial_relative_coordinate[0].rotated(
            angle_anchor
        )
        angle_entity = angle_anchor + self.initial_relative_coordinate[1]

        self.pm_body.position = position_entity
        self.pm_body.angle = angle_entity

        self.pm_body.velocity = 0, 0
        self.pm_body.angular_velocity = 0
        self.pm_body.force = (0, 0)
        self.pm_body.torque = 0

        if hasattr(self, "motor") and self.motor is not None:
            self.motor.rate = 0

        if self.pm_body.space:
            self.pm_body.space.reindex_shapes_for_body(self.pm_body)

    def _get_joint(self):
        pass

    def _get_limit(self):
        pass

    def _get_motor(self):
        pass

    def _get_pm_body(self):
        vertices = self.sprite.get_hit_box()
        moment = pymunk.moment_for_poly(self.mass, vertices)
        return pymunk.Body(self.mass, moment, body_type=pymunk.Body.DYNAMIC)
