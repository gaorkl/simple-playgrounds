from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from arcade import SpriteList
from arcade.sprite import Sprite

from ..entity import InteractiveEntity, PhysicalEntity

if TYPE_CHECKING:
    from ..entity import EmbodiedEntity
    from ..playground import Playground


class TopDownView:
    def __init__(
        self,
        playground: Playground,
        size: Optional[Tuple[int, int]] = None,
        center: Tuple[float, float] = (0, 0),
        zoom: float = 1,
        display_uid: bool = False,
        draw_transparent: bool = True,
        draw_interactive: bool = True,
    ) -> None:

        self._playground = playground

        self._ctx = playground.window.ctx

        self._center = center

        if not size:
            size = playground.size

        if not size:
            raise ValueError("Size should be set")

        self._width, self._height = self._size = size

        self._zoom = zoom
        self._draw_transparent = draw_transparent
        self._draw_interactive = draw_interactive
        self._display_uid = display_uid

        self._transparent_sprites = SpriteList()
        self._visible_sprites = SpriteList()
        self._interactive_sprites = SpriteList()
        self._traversable_sprites = SpriteList()

        self._background = playground.background

        self._fbo = self._ctx.framebuffer(
            color_attachments=[
                self._ctx.texture(
                    (size),
                    components=4,
                    wrap_x=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    wrap_y=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    # type: ignore
                    filter=(self._ctx.NEAREST, self._ctx.NEAREST),
                ),
            ]
        )

        self._sprites: Dict[EmbodiedEntity, Sprite] = {}

        self._playground.add_view(self)

    @property
    def zoom(self):
        return self._zoom

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def center(self):
        return self._center

    @property
    def sprites(self):
        return self._sprites

    def add(self, entity):

        if isinstance(entity, PhysicalEntity):

            sprite = entity.get_sprite(self._zoom, color_uid=self._display_uid)

            if entity.traversable:
                self._traversable_sprites.append(sprite)

            elif entity.transparent:
                if self._draw_transparent:
                    self._transparent_sprites.append(sprite)

            else:
                self._visible_sprites.append(sprite)

        elif isinstance(entity, InteractiveEntity):

            if not self._draw_interactive:
                return

            if self._display_uid:
                raise ValueError(
                    "Cannot display uid of interactive, set draw_interactive to False"
                )

            sprite = entity.get_sprite(self._zoom)
            self._interactive_sprites.append(sprite)

        else:
            raise ValueError("Not implemented")

        entity.update_sprite(self, sprite)
        self._sprites[entity] = sprite

    def remove(self, entity):

        sprite = self._sprites.pop(entity)

        if isinstance(entity, PhysicalEntity):

            if entity.traversable:
                self._traversable_sprites.remove(sprite)

            elif entity.transparent:
                self._transparent_sprites.remove(sprite)

            else:
                self._visible_sprites.remove(sprite)

        elif isinstance(entity, InteractiveEntity):

            self._interactive_sprites.remove(sprite)

    def update_sprites(self, force=False):

        # check that
        for entity, sprite in self._sprites.items():
            if entity.needs_sprite_update or force:
                entity.update_sprite(self, sprite)

    def update(self, force=False):

        self.update_sprites(force)

        with self._fbo.activate() as fbo:
            fbo.clear(self._background)

            # Change projection to match the contents
            self._ctx.projection_2d = 0, self._width, 0, self._height

            self._transparent_sprites.draw(pixelated=True)
            self._interactive_sprites.draw(pixelated=True)
            self._visible_sprites.draw(pixelated=True)
            self._traversable_sprites.draw(pixelated=True)

    def get_np_img(self):
        img = np.frombuffer(self._fbo.read(), dtype=np.dtype("B")).reshape(
            self._height, self._width, 3
        )
        return img

    def draw(self):
        img = self.get_np_img()
        plt.imshow(img)
        plt.axis("off")
        plt.show()

    def reset(self):

        self._transparent_sprites.clear()
        self._interactive_sprites.clear()
        self._visible_sprites.clear()
        self._traversable_sprites.clear()
