from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.position_utils import Coordinate
    from simple_playgrounds.entity.entity import EmbodiedEntity

import numpy as np
from matplotlib import pyplot as plt
# plt.rcParams.update({'figure.max_open_warning': 0})


class View(ABC):

    def __init__(self,
                 size_on_playground: Tuple[int, int],
                 view_size: Optional[Tuple[int, int]] = None,
                 draw_transparent: Optional[bool] = False,
                 draw_interaction: Optional[bool] = False,
                 **kwargs):

        self._size_on_playground = size_on_playground
        self._playground: Optional[Playground] = None

        if view_size:
            self._view_size = view_size
        else:
            self._view_size = self._size_on_playground

        self._create_fig(**kwargs)

        self._draw_transparent = draw_transparent
        self._draw_interaction = draw_interaction

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
