"""
Module for Texture of SceneElements and Parts of Agents.
Documentation is incomplete/missing. Refer to the tutorials for now.
"""

import itertools
import math
from abc import ABC, abstractmethod
from typing import Union, Tuple, Dict, Callable, Optional

import numpy as np
from pygame import Surface, draw
from pygame import surfarray
from skimage.transform import resize


class Texture(ABC):
    """ Base Class for Textue"""
    def __init__(
        self,
    ):

        self._size = None
        self._surface = None

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: Union[Tuple[float, float], float, int]):

        if isinstance(size, (tuple, list)):

            assert len(size) == 2

            # make sure size is even
            w = int(size[1] / 2) * 2 + 5
            h = int(size[0] / 2) * 2 + 5

            self._size = w, h

        elif isinstance(size, (float, int)):

            # convert radius into w/l
            w = 2 * int(size * math.sqrt(2)) + 5

            self._size = w, w

        else:
            raise ValueError('Texture size not compatible')

        self._surface = Surface(self._size)

    @abstractmethod
    def generate(self):
        """ Generates a pygame surface at the correct dimension"""
        if not self._size:
            raise ValueError("The texture surface was not instantiated. The size is not set.")

    @property
    @abstractmethod
    def base_color(self):
        """
        Base color for display.

        Returns: tuple of colors

        """
        ...

    def get_pixel(self, rel_pos: Tuple[float, float]):

        x = int(rel_pos[0] + (self._size[0] - 1) / 2)
        y = int(rel_pos[1] + (self._size[1] - 1) / 2)

        x = min(max(0, x), self._size[0] - 1)
        y = min(max(0, y), self._size[1] - 1)

        return self._surface.get_at((x, y))[:3]

    @property
    def surface(self):
        return self._surface


class TextureGenerator:
    """
    Class to register Textures.
    """

    subclasses: Dict[str, Callable] = {}

    @classmethod
    def register_subclass(cls, texture_type):
        """ Registers a class Texture """
        def decorator(subclass):

            cls.subclasses[texture_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, **params):
        """ Create a new instance of Class Texture based on its parameters."""

        texture_type = params.pop('texture_type')

        if texture_type not in cls.subclasses:
            raise ValueError('Texture not implemented: ' + texture_type)

        return cls.subclasses[texture_type](**params)


@TextureGenerator.register_subclass('color')
class ColorTexture(Texture):
    """ Simple Uniform texture of a single color"""
    def __init__(
        self,
        color: Tuple[int, int, int],
    ):

        assert len(color) == 3

        super().__init__()
        self._color = color

    def generate(self):
        super().generate()
        self._surface.fill(self._color)
        return self._surface

    @property
    def base_color(self):
        return self._color


@TextureGenerator.register_subclass('unique_centered_stripe')
class UniqueCenteredStripeTexture(ColorTexture):
    def __init__(
        self,
        color,
        color_stripe: Tuple[int, int, int],
        size_stripe,
    ):

        super().__init__(color=color)

        assert len(color_stripe) == 3

        self._color_stripe = color_stripe
        self._size_stripe = size_stripe

    def generate(self):
        super().generate()
        draw.line(
            self._surface,
            color=self._color_stripe,
            start_pos=(self._size[0] / 2, self._size[1] / 2),
            end_pos=(self._size[0] / 2, self._size[1]),
            width=5,
        )

        return self._surface


@TextureGenerator.register_subclass('multiple_centered_stripes')
class MultipleCenteredStripesTexture(Texture):
    def __init__(
        self,
        color_1: Tuple[int, int, int],
        color_2: Tuple[int, int, int],
        n_stripes: int,
    ):

        super().__init__()

        assert len(color_1) == 3
        self._color_1 = color_1

        assert len(color_2) == 3
        self._color_2 = color_2

        assert n_stripes > 1
        self.n_stripes = n_stripes

    def generate(self):
        """
        Generate a pygame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """
        super().generate()
        img = np.zeros((*self._size, 3))

        x = (self._size[0] - 1) / 2
        y = (self._size[1] - 1) / 2

        for i in range(self._size[0]):
            for j in range(self._size[1]):

                angle = (np.arctan2(j - y, i - x) - math.pi / self.n_stripes /
                         2.) % (2 * math.pi / self.n_stripes)

                if angle > math.pi / self.n_stripes:
                    img[i, j, :] = self._color_1
                else:
                    img[i, j, :] = self._color_2

        self._surface = surfarray.make_surface(img)

        return self._surface

    @property
    def base_color(self):
        return self._color_1


class RandomTexture(Texture, ABC):
    def __init__(
        self,
        rng: Optional[np.random.Generator] = None,
    ):

        if not rng:
            rng = np.random.default_rng()
        self._rng = rng

        super().__init__()


@TextureGenerator.register_subclass('random_uniform')
class RandomUniformTexture(RandomTexture):
    """ Random Uniform Texture."""
    def __init__(
        self,
        color_min: Tuple[int, int, int],
        color_max: Tuple[int, int, int],
        rng=None,
    ):

        assert len(color_min) == 3
        assert len(color_max) == 3

        super().__init__(rng)

        self._min = color_min
        self._max = color_max

    def generate(self):
        super().generate()
        random_image = self._rng.uniform(self._min, self._max,
                                         (*self._size, 3))
        random_image = random_image.astype('int')
        surf = surfarray.make_surface(random_image)
        self._surface = surf
        return self._surface

    @property
    def base_color(self):

        mean_color = [(a + b) / 2 for a, b in zip(self._min, self._max)]

        return mean_color


@TextureGenerator.register_subclass('random_tiles')
class RandomTilesTexture(RandomTexture):
    def __init__(
        self,
        size_tiles,
        color_min: Tuple[int, int, int],
        color_max: Tuple[int, int, int],
        rng=None,
    ):

        assert len(color_min) == 3
        assert len(color_max) == 3

        super().__init__(rng)

        self._size_tiles = size_tiles
        self._min = color_min
        self._max = color_max

    def generate(self):

        super().generate()

        shape_mini = (max(1, int(self._size[0] * 1.0 / self._size_tiles)),
                      max(1, int(self._size[1] * 1.0 / self._size_tiles)), 3)

        random_image = self._rng.uniform(self._min, self._max,
                                         shape_mini).astype('int')
        random_image = resize(random_image,
                              self._size,
                              order=0,
                              preserve_range=True)
        surf = surfarray.make_surface(random_image)
        self._surface = surf
        return self._surface

    @property
    def base_color(self):
        mean_color = [(a + b) / 2 for a, b in zip(self._min, self._max)]

        return mean_color


@TextureGenerator.register_subclass('centered_random_tiles')
class CenteredRandomTilesTexture(RandomTexture):
    def __init__(
        self,
        size_tiles,
        color_min: Tuple[int, int, int],
        color_max: Tuple[int, int, int],
        rng=None,
    ):

        assert len(color_min) == 3
        assert len(color_max) == 3

        super().__init__(rng)

        self._size_tiles = size_tiles
        self._min = color_min
        self._max = color_max

    def generate(self):
        super().generate()

        assert self._size_tiles <= self._size[0] and self._size_tiles <= self._size[1]

        radius = max(self._size)
        n_stripes = int(2 * math.pi * radius / self._size_tiles)

        img = np.zeros((*self._size, 3))

        colors = [[
            self._rng.integers(self._min[i], self._max[i], endpoint=True)
            for i in range(3)
        ] for _ in range(n_stripes)]

        x = (self._size[0] - 1) / 2
        y = (self._size[1] - 1) / 2

        for i in range(self._size[0]):
            for j in range(self._size[1]):

                angle = int(
                    np.arctan2(j - y, i - x) / (2 * math.pi / n_stripes))

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        self._surface = surf
        return self._surface

    @property
    def base_color(self):

        mean_color = [(a + b) / 2 for a, b in zip(self._min, self._max)]

        return mean_color


@TextureGenerator.register_subclass('list_centered_random_tiles')
class ListCenteredRandomTilesTexture(RandomTexture):
    def __init__(
        self,
        size_tiles,
        colors: Tuple[Tuple[int, int, int], ...],
        rng: Optional[np.random.Generator] = None,
    ):

        super().__init__(rng)

        for color in colors:
            assert len(color) == 3

        self._colors = colors
        self._size_tiles = size_tiles

    def generate(self):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """
        super().generate()

        radius = max(self._size)
        n_stripes = int(2 * math.pi * radius / self._size_tiles)

        img = np.zeros((*self._size, 3))

        colors = self._rng.choice(self._colors,
                                  size=n_stripes,
                                  replace=True)

        x = (self._size[0] - 1) / 2
        y = (self._size[1] - 1) / 2

        for i in range(self._size[0]):
            for j in range(self._size[1]):

                angle = int(
                    np.arctan2(j - y, i - x) / (2 * math.pi / n_stripes))

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        self._surface = surf
        return self._surface

    @property
    def base_color(self):
        return 125, 25, 90


@TextureGenerator.register_subclass('unique_random_tiles')
class UniqueRandomTilesTexture(RandomTexture):
    def __init__(self,
                 n_colors=10,
                 range_unique_color=5,
                 size_tiles=4,
                 color_min=(0, 0, 0),
                 color_max=(255, 255, 255),
                 rng: Optional[np.random.Generator] = None):

        super().__init__(rng=rng)

        # Compute colors
        n_color_splits = int(n_colors**(1 / 3))

        r_list = [
            color_min[0] + n_r * (color_max[0] - color_min[0]) /
            (n_color_splits - 1) for n_r in range(n_color_splits)
        ]
        g_list = [
            color_min[1] + n_g * (color_max[1] - color_min[1]) /
            (n_color_splits - 1) for n_g in range(n_color_splits)
        ]
        b_list = [
            color_min[2] + n_b * (color_max[2] - color_min[2]) /
            (n_color_splits - 1) for n_b in range(n_color_splits)
        ]

        list_all_colors = itertools.product(r_list, g_list, b_list)

        self.all_textures = []

        for color in list_all_colors:

            color_min = tuple(
                int(c) - int(range_unique_color / 2.) for c in color)
            color_max = tuple(
                int(c) + int(range_unique_color / 2.) for c in color)

            text = RandomTilesTexture(size_tiles=size_tiles,
                                      color_min=color_min,
                                      color_max=color_max,
                                      rng=rng)
            self.all_textures.append(text)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        for text in self.all_textures:
            text.size = size

        self._size = size

    def generate(self):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """
        super().generate()
        text = self._rng.choice(self.all_textures)
        return text.generate()

    @property
    def base_color(self):
        return 125, 25, 90
