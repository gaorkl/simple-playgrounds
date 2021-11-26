from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np

from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.common.position_utils import Coordinate
from simple_playgrounds.entity.entity import EmbodiedEntity

class View(ABC):

    def __init__(self,
                 playground: Playground,
                 size_on_playground: Optional[Tuple[int, int]] = None,
                 view_size: Optional[Tuple[int, int]] = None,
                 zoom_ratio: Optional[float] = None,
                 ):

        self._playground = playground

        # Define the size of the view on the playground
        if not size_on_playground:
            if not self._playground.size:
                raise ValueError('Size of view should be set')
            self._size_on_playground = self._playground.size

        # Define the output size
        if view_size and zoom_ratio:
            raise ValueError('Both view_size and zoom_factor are set')

        if view_size:
            self._view_size = view_size
        elif zoom_ratio:
            self._view_size = (size*zoom_ratio for size in size_on_playground)
        else:
            raise ValueError('Either view_size and zoom_factor are set')

        self._center_coordinate: Optional[Coordinate] = None
        self._image_view = np.ndarray(shape=(*self._view_size, 3), dtype=np.uint8)

    @property
    @abstractmethod
    def _center_coordinates(self):
        ...

    @abstractmethod
    def update_view(self):
        ...

    @property
    def shape(self):
        return self._image_view.shape

    @property
    def size(self):
        return self._view_size


class FixedGlobalView(View):

    def __init__(self, coordinates: Coordinate, **kwargs):

        self._coordinates = coordinates
        super().__init__(**kwargs)

    def update_view(self):
        pass

    @property
    def _center_coordinates(self):
        return self._coordinates


class AnchoredView(View):

    def __init__(self, anchor: EmbodiedEntity, **kwargs):

        self._anchor = anchor
        super().__init__(**kwargs)

    def update_view(self):
        pass

    @property
    def _center_coordinates(self):
        return self._anchor.coordinates
