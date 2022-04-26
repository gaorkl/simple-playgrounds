from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.position_utils import Coordinate
    from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity

import numpy as np
import arcade


class View(ABC):

    def __init__(self,
                 playground: Playground,
                 size: Tuple[int, int],
                 center: Tuple[int, int] = (0, 0),
                 zoom: float = 1,
                 draw_transparent: Optional[int] = None,
                 draw_interaction: Optional[int] = None,
                 draw_uids: Optional[bool] = False,
                 **kwargs):

        self._playground = playground

        self._size = size
        self._center = center
        self._zoom = zoom

        self._draw_transparent = draw_transparent
        self._draw_interaction = draw_interaction
        self._draw_uids = draw_uids

        self._playground.add_view(self)

    def add_sprite(self, view: View):

        if view in self._sprites:
            raise ValueError('Sprite already added to view')

        sprite = self._get_sprite(view.zoom, view.color_with_uid)
        self._sprites[view] = sprite
        self._update_sprite_position(view)
        
        return sprite


    def update_sprites(self, force=False):
      
        moving = False
        if self.velocity != (0, 0) or self.angular_velocity != 0:
            moving = True

                if self._moved or moving or force:

            for view in self._sprites:
                self._update_sprite_position(view)


    def _update_sprite_position(self, view):

        sprite = self._sprites[view]

        pos_x = (self.position.x - view.center[0])*view.zoom + view.width // 2
        pos_y = (self.position.y - view.center[1])*view.zoom + view.height // 2
        
        sprite.set_position(pos_x, pos_y)
        sprite.angle = int(self.angle*180/math.pi)


    def _create_fig(self, background_color: Optional[str] = 'black'):

        # check that input and output have same scale ratio
        if self._view_size[0] / self._size_on_playground[0] != self._view_size[1] / self._size_on_playground[1]:
            raise ValueError('Size of area covered on playground and output image should be the same.')
        self._zoom = self._view_size[0] / self._size_on_playground[0]
        # Matplotlib things
        fig, ax = plt.subplots(facecolor=background_color)

        size = (self._view_size[0]/100, self._view_size[1]/100)
        # fig.set_frameon(False)``
        fig.set_dpi(100)
        fig.set_size_inches(size, forward=True)
        # fig.frameon = False

        lim_x = self._size_on_playground[0]/2
        lim_y = self._size_on_playground[1]/2

        ax.axis('off')
        #
        ax.autoscale_view('tight')
        ax = plt.axes([0, 0, 1, 1], frameon=False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        ax.set_facecolor(background_color)
        ax.set_ylim(-lim_y, lim_y)
        ax.set_xlim(-lim_x, lim_x)
        self._ax = ax
        self._canvas = fig.canvas

        self._fig = fig

        self._canvas.draw()

    def add_patch(self, patch):

        self._ax.add_patch(patch)

    def draw_patch(self, patch):

        self._ax.draw_artist(patch)

    def update_view(self):

        self._canvas.draw()

        assert self._playground
        for entity in self._playground.physical_entities:
            if entity.transparent:
                if self._draw_transparent:
                    entity.update_view(self)
            else:
                entity.update_view(self)

        if self._draw_interaction:
            for entity in self._playground.interactive_entities:
                entity.update_view(self)

        self._canvas.blit(self._fig.bbox)
        self._canvas.flush_events()

        image_from_plot = np.frombuffer(self._canvas.tostring_rgb(), dtype=np.uint8)
        image_from_plot = image_from_plot.reshape(self._canvas.get_width_height()[::-1] + (3,))

        return image_from_plot

    @property
    def size(self):
        return self._view_size

    @property
    def zoom(self):
        return self._zoom

    @property
    @abstractmethod
    def center_coordinates(self):
        ...

    @property
    def position(self):
        return self.center_coordinates[0]

    @property
    def angle(self):
        return self.center_coordinates[1]

    @property
    def canvas(self):
        return self._canvas
   
    def __del__(self):
        plt.close(self._fig)

class FixedGlobalView(View):

    def __init__(self, playground: Playground, coordinates: Coordinate, **kwargs):


        # Define the size of the view on the playground
        if not kwargs.get('size_on_playground', None):
            if playground.size:
                kwargs['size_on_playground'] = playground.size
            else:
                raise ValueError('Size of view should be set')
        
        self._coordinates = coordinates
        super().__init__(**kwargs)

        self._playground = playground

    @property
    def center_coordinates(self):
        return self._coordinates


class AnchoredView(View):

    def __init__(self, anchor: EmbodiedEntity, **kwargs):

        self._anchor = anchor
        assert self._anchor.playground

        super().__init__(**kwargs)
        self._playground = self._anchor.playground

    @property
    def center_coordinates(self):
        return self._anchor.coordinates
