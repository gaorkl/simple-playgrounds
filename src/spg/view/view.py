from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Union, Dict
from arcade.sprite import Sprite
from spg.agent.agent import Agent
from spg.agent.part import PhysicalPart
from spg.element.element import SceneElement
from spg.entity import InteractiveEntity, PhysicalEntity

if TYPE_CHECKING:
    from spg.playground import Playground
    from spg.entity import EmbodiedEntity

import numpy as np
import arcade

import matplotlib.pyplot as plt


class TopDownView(ABC):
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

        self._transparent_sprites = arcade.SpriteList()
        self._visible_sprites = arcade.SpriteList()
        self._interactive_sprites = arcade.SpriteList()
        self._traversable_sprites = arcade.SpriteList()

        self._background = playground.background

        self._fbo = self._ctx.framebuffer(
            color_attachments=[
                self._ctx.texture(
                    (size),
                    components=4,
                    wrap_x=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    wrap_y=self._ctx.CLAMP_TO_BORDER,  # type: ignore
                    filter=(self._ctx.NEAREST, self._ctx.NEAREST),  # type: ignore
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
            if entity.needs_sprite_update:
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

    # def flip(self):
    #     self._fbo.flip()
    # super().flip()

    # def imdisplay(self):
    #     array = np.frombuffer(self._fbo.read(), dtype=np.dtype("B")).reshape(
    #         self._height, self._width, 3
    #     )
    #     array = array[::-1, :]
    #     img = Image.fromarray(array, "RGB")
    #     ImageShow.show(img, "test")

    def reset(self):

        self._transparent_sprites.clear()
        self._interactive_sprites.clear()
        self._visible_sprites.clear()
        self._traversable_sprites.clear()


# class PlaygroundView(AbstractView):

# class PlaygroundView(TopDownView):
#         super().__init__(playground, size, center, zoom, display_uid, draw_transparent, draw_interactive)

#         self._playground.set_size(size)

#     def update(self, force=False):
#         # self.ctx.projection_2d = 0, self.width, 0, self.height
# class TopDownView(AbstractView):


#    def __init__(self,
#                 playground: Playground,
#                 size: Tuple[int, int],
#                 center: Tuple[int, int] = (0, 0),
#                 zoom: float = 1,
#                 draw_transparent: Optional[int] = None,
#                 draw_interaction: Optional[int] = None,
#                 draw_uids: Optional[bool] = False,
#                 **kwargs):

#        self._playground = playground

#        self._size = size
#        self._center = center
#        self._zoom = zoom

#        self._draw_transparent = draw_transparent
#        self._draw_interaction = draw_interaction
#        self._draw_uids = draw_uids

#        self._playground.add_view(self)

#    def add_sprite(self, view: View):

#        if view in self._sprites:
#            raise ValueError('Sprite already added to view')

#        sprite = self._get_sprite(view.zoom, view.color_with_uid)
#        self._sprites[view] = sprite
#        self._update_sprite_position(view)

#        return sprite


#    def update_sprites(self, force=False):

#        moving = False
#        if self.velocity != (0, 0) or self.angular_velocity != 0:
#            moving = True

#                if self._moved or moving or force:

#            for view in self._sprites:
#                self._update_sprite_position(view)


#    def _update_sprite_position(self, view):

#        sprite = self._sprites[view]

#        pos_x = (self.position.x - view.center[0])*view.zoom + view.width // 2
#        pos_y = (self.position.y - view.center[1])*view.zoom + view.height // 2

#        sprite.set_position(pos_x, pos_y)
#        sprite.angle = int(self.angle*180/math.pi)


#    def _create_fig(self, background_color: Optional[str] = 'black'):

#        # check that input and output have same scale ratio
#        if self._view_size[0] / self._size_on_playground[0] != self._view_size[1] / self._size_on_playground[1]:
#            raise ValueError('Size of area covered on playground and output image should be the same.')
#        self._zoom = self._view_size[0] / self._size_on_playground[0]
#        # Matplotlib things
#        fig, ax = plt.subplots(facecolor=background_color)

#        size = (self._view_size[0]/100, self._view_size[1]/100)
#        # fig.set_frameon(False)``
#        fig.set_dpi(100)
#        fig.set_size_inches(size, forward=True)
#        # fig.frameon = False

#        lim_x = self._size_on_playground[0]/2
#        lim_y = self._size_on_playground[1]/2

#        ax.axis('off')
#        #
#        ax.autoscale_view('tight')
#        ax = plt.axes([0, 0, 1, 1], frameon=False)
#        ax.get_xaxis().set_visible(False)
#        ax.get_yaxis().set_visible(False)

#        ax.set_facecolor(background_color)
#        ax.set_ylim(-lim_y, lim_y)
#        ax.set_xlim(-lim_x, lim_x)
#        self._ax = ax
#        self._canvas = fig.canvas

#        self._fig = fig

#        self._canvas.draw()

#    def add_patch(self, patch):

#        self._ax.add_patch(patch)

#    def draw_patch(self, patch):

#        self._ax.draw_artist(patch)

#    def update_view(self):

#        self._canvas.draw()

#        assert self._playground
#        for entity in self._playground.physical_entities:
#            if entity.transparent:
#                if self._draw_transparent:
#                    entity.update_view(self)
#            else:
#                entity.update_view(self)

#        if self._draw_interaction:
#            for entity in self._playground.interactive_entities:
#                entity.update_view(self)

#        self._canvas.blit(self._fig.bbox)
#        self._canvas.flush_events()

#        image_from_plot = np.frombuffer(self._canvas.tostring_rgb(), dtype=np.uint8)
#        image_from_plot = image_from_plot.reshape(self._canvas.get_width_height()[::-1] + (3,))

#        return image_from_plot

#    @property
#    def size(self):
#        return self._view_size

#    @property
#    def zoom(self):
#        return self._zoom

#    @property
#    @abstractmethod
#    def center_coordinates(self):
#        ...

#    @property
#    def position(self):
#        return self.center_coordinates[0]

#    @property
#    def angle(self):
#        return self.center_coordinates[1]

#    @property
#    def canvas(self):
#        return self._canvas

#    def __del__(self):
#        plt.close(self._fig)

# class FixedGlobalView(View):

#    def __init__(self, playground: Playground, coordinates: Coordinate, **kwargs):


#        # Define the size of the view on the playground
#        if not kwargs.get('size_on_playground', None):
#            if playground.size:
#                kwargs['size_on_playground'] = playground.size
#            else:
#                raise ValueError('Size of view should be set')

#        self._coordinates = coordinates
#        super().__init__(**kwargs)

#        self._playground = playground

#    @property
#    def center_coordinates(self):
#        return self._coordinates


# class AnchoredView(View):

#    def __init__(self, anchor: EmbodiedEntity, **kwargs):

#        self._anchor = anchor
#        assert self._anchor.playground

#        super().__init__(**kwargs)
#        self._playground = self._anchor.playground

#    @property
#    def center_coordinates(self):
#        return self._anchor.coordinates
