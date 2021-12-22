from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import pymunk

if TYPE_CHECKING:
    from simple_playgrounds.entity.embodied.contour import Contour

from abc import ABC, abstractmethod
import numpy as np
import math
from skimage.transform import rotate

Pixel = Tuple[int, int, int]


class Appearance(ABC):

    def __init__(self):

        self._contour: Optional[Contour] = None
        self._image_mask: Optional[np.ndarray] = None

    @property
    @abstractmethod
    def base_color(self) -> Pixel:
        """
        Base color for display.

        Returns: Pixel, RBG tuple of ints.

        """
        ...

    @abstractmethod
    def get_pixel(self,
                  orig: pymunk.Vec2d,
                  normal: pymunk.Vec2d
                  ) -> Pixel:
        """
        Get the pixel value of the appearance based on intersection with a line
        defined by an origin and normal vector.
        Pixel is a tuple of ints (R,G,B).

        Args:
            orig:
            normal:

        Returns:

        """

    def generate_image_mask(self, angle: float):
        return rotate(self._image_mask, angle*180/math.pi, order=1)

    @property
    def contour(self):
        return self._contour

    @contour.setter
    def contour(self, cont):
        self._contour = cont


    # def get_pixel(self, rel_pos: Tuple[float, float]):
    #     x = int(rel_pos[0]) + self._contour.mask_size[0]
    #     y = int(rel_pos[1]) + self._contour.mask_size[1]
    #
    #     x = min(max(0, x), self._contour.mask_size[0] - 1)
    #     y = min(max(0, y), self._contour.mask_size[1] - 1)
    #
    #     return self._image_mask[x, y]


