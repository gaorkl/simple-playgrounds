from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.position_utils import Coordinate
    from simple_playgrounds.entity.entity import EmbodiedEntity

import numpy as np
from matplotlib import pyplot as plt


class View(ABC):

    def __init__(self,
                 playground: Playground,
                 size_on_playground: Optional[Tuple[int, int]] = None,
                 view_size: Optional[Tuple[int, int]] = None,
                 background_color: Optional[str] = 'black'
                 ):

        self._playground = playground

        # Define the size of the view on the playground
        if size_on_playground:
            self._size_on_playground = size_on_playground
        elif self._playground.size:
            self._size_on_playground = self._playground.size
        else:
            raise ValueError('Size of view should be set')

        if view_size:
            self._view_size = view_size
        else:
            self._view_size = self._size_on_playground

        # check that input and output have same scale ratio
        if self._view_size[0] / self._size_on_playground[0] != self._view_size[1] / self._size_on_playground[1]:
            raise ValueError('Size of area covered on playground and output image should be the same.')
        self._zoom = self._view_size[0] / self._size_on_playground[0]

        # Matplotlib things
        fig, ax = plt.subplots(facecolor=background_color)

        size = (self._size_on_playground[0]/100, self._size_on_playground[1]/100)
        # fig.set_frameon(False)
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

    @abstractmethod
    def update_view(self):
        ...

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


class FixedGlobalView(View):

    def __init__(self, coordinates: Coordinate, **kwargs):

        self._coordinates = coordinates
        super().__init__(**kwargs)

    def update_view(self):

        self._canvas.draw()

        for entity in self._playground._physical_entities:
            entity.update_view(self)

        self._canvas.blit(self._fig.bbox)

        self._canvas.flush_events()
        image_from_plot = np.frombuffer(self._canvas.tostring_rgb(), dtype=np.uint8)
        image_from_plot = image_from_plot.reshape(self._canvas.get_width_height()[::-1] + (3,))

        return image_from_plot

    @property
    def center_coordinates(self):
        return self._coordinates


class AnchoredView(View):

    def __init__(self, anchor: EmbodiedEntity, **kwargs):

        self._anchor = anchor
        super().__init__(**kwargs)

    def update_view(self):
        pass

    @property
    def center_coordinates(self):
        return self._anchor.coordinates
