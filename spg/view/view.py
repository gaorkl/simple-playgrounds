from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict, Tuple, Union

import arcade
import numpy as np

if TYPE_CHECKING:
    from ..playground import Playground

from ..entity import Agent, Element, Entity


class View:

    updated = False

    def __init__(
        self,
        playground: Playground,
        size_on_playground: Tuple[int, int],
        scale: float = 1,
        center: Tuple[float, float] = (0, 0),
        uid_mode: bool = False,
        draw_transparent: bool = True,
    ) -> None:

        self.playground = playground

        self._ctx = playground.ctx
        self.center = center

        self.scale = scale
        self.size = int(size_on_playground[0] * scale), int(
            size_on_playground[1] * scale
        )
        self.width, self.height = self.size

        # Change projection to match the contents
        self._ctx.projection_2d = 0, self.width, 0, self.height

        self.draw_transparent = draw_transparent
        self.uid_mode = uid_mode

        self._fbo = self._ctx.framebuffer(
            color_attachments=[
                self._ctx.texture(
                    self.size,
                    components=4,
                    wrap_x=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    wrap_y=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    filter=(self._ctx.NEAREST, self._ctx.NEAREST),
                ),
            ]
        )

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("traversable")
        self.scene.add_sprite_list("entity")

        self.entity_to_sprites: Dict[Entity, arcade.Sprite] = {}

        for element in playground.elements:
            self.add(element)

        for agent in playground.agents:
            self.add(agent)

        self.playground.views.append(self)

    @property
    def texture(self):
        """The OpenGL texture containing the map pixel data"""
        return self._fbo.color_attachments[0]

    def add(self, entity: Union[Element, Agent]):

        if entity.transparent and not self.draw_transparent:
            pass

        elif entity not in self.entity_to_sprites:
            sprite = entity.get_sprite(self.scale, color_uid=self.uid_mode)

            self.entity_to_sprites[entity] = sprite

            self._add_sprite_to_scene(sprite, entity)

        if isinstance(entity, (Agent, Element)):
            for attached in entity.all_attached:
                self.add(attached)

    def _add_sprite_to_scene(self, sprite, entity):

        if entity.traversable:
            self.scene.add_sprite("traversable", sprite)
        else:
            self.scene.add_sprite("entity", sprite)

    def remove(self, entity):

        sprite = self.entity_to_sprites.pop(entity)

        self._remove_sprite_from_scene(sprite, entity)

        if isinstance(entity, (Agent, Element)):
            for attached in entity.all_attached:
                self.remove(attached)

    def _remove_sprite_from_scene(self, sprite, entity):

        if entity.traversable:
            sprite_list = self.scene.get_sprite_list("traversable")
            sprite_list.remove(sprite)
        else:
            sprite_list = self.scene.get_sprite_list("entity")
            sprite_list.remove(sprite)

    def update_sprites(self, force=False):

        for entity, sprite in self.entity_to_sprites.items():
            pos_x = (
                entity.pm_body.position.x - self.center[0]
            ) * self.scale + self.width // 2
            pos_y = (
                entity.pm_body.position.y - self.center[1]
            ) * self.scale + self.height // 2

            if sprite.position != (pos_x, pos_y) or force:
                sprite.set_position(pos_x, pos_y)
                sprite.angle = int(entity.pm_body.angle * 180 / math.pi)

    def update(self, force=False):

        self.update_sprites(force)

        with self._fbo.activate() as fbo:

            if self.uid_mode:
                fbo.clear()
            else:
                fbo.clear(self.playground.background)

            self.scene.draw(names=["entity", "traversable"])
        self.updated = True

    def get_np_img(self):

        if not self.updated:
            self.update()

        img = np.frombuffer(self._fbo.read(), dtype=np.dtype("B")).reshape(
            self.height, self.width, 3
        )
        return img

    def reset(self):
        self.scene.remove_sprite_list_by_name("entity")
        self.scene.remove_sprite_list_by_name("traversable")
        self.scene.add_sprite_list("traversable")
        self.scene.add_sprite_list("entity")

        self.entity_to_sprites = {}
