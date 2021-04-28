"""
Module for Texture of SceneElements and Parts of Agents.
Documentation is incomplete/missing. Refer to the tutorials for now.
"""

from typing import Union, Tuple, List, Dict, Callable

from abc import ABC, abstractmethod
import math

import numpy as np
from pygame import Surface, draw
from pygame import surfarray
from skimage.transform import resize


class Texture(ABC):
    """ Base Class for Textue"""
    def __init__(
        self,
        size: Union[List[float], Tuple[float, float], float],
    ):

        if isinstance(size, (tuple, list)):
            assert len(size) == 2
            self._size = int(size[1]) + 5, int(size[0]) + 5

        elif isinstance(size, int):
            self._size = (int(size + 5), int(size + 5))

        else:
            raise ValueError('Texture size not compatible')

        self._surface = Surface(self._size)

    @abstractmethod
    def generate(self):
        """ Generates a pygame surface at the correct dimension"""

    def get_pixel(self, rel_pos):

        x = int(rel_pos[0] + self._size[0])
        y = int(rel_pos[1] + self._size[1])

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
        size,
        color: Union[Tuple[int, int, int], List[int]],
    ):

        assert isinstance(color, (tuple, list))
        assert len(color) == 3

        super().__init__(size)
        self._color = color

    def generate(self):
        self._surface.fill(self._color)
        return self._surface


@TextureGenerator.register_subclass('unique_polar_stripe')
class UniqueCenteredStripeTexture(ColorTexture):
    def __init__(
        self,
        size,
        color,
        color_stripe: Union[Tuple[int, int, int], List[int]],
        size_stripe,
    ):

        super().__init__(size, color)

        assert isinstance(color_stripe, (tuple, list))
        assert len(color_stripe) == 3

        self._color_stripe = color_stripe
        self._size_stripe = size_stripe

    def generate(self):
        self._surface.fill(self._color)
        draw.line(
            self._surface,
            color=self._color_stripe,
            start_pos=(self._size[0] / 2, self._size[1] / 2),
            end_pos=(self._size[0] / 2, self._size[1]),
            width=5,
        )

        return self._surface


class RandomTexture(Texture, ABC):
    def __init__(
        self,
        size,
        rng: Union[np.random.Generator, None] = None,
    ):

        self._rng = rng
        if not rng:
            self._rng = np.random.default_rng()

        super().__init__(size)


@TextureGenerator.register_subclass('random_uniform')
class RandomUniformTexture(RandomTexture):
    """ Random Uniform Texture."""
    def __init__(
        self,
        size,
        color_min: Union[Tuple[int, int, int], List[int]],
        color_max: Union[Tuple[int, int, int], List[int]],
        rng=None,
    ):

        assert isinstance(color_min, (tuple, list))
        assert len(color_min) == 3

        assert isinstance(color_max, (tuple, list))
        assert len(color_max) == 3

        super().__init__(size, rng)

        self._min = color_min
        self._max = color_max

    def generate(self):

        random_image = self._rng.uniform(self._min, self._max,
                                         (*self._size, 3))
        random_image = random_image.astype('int')
        surf = surfarray.make_surface(random_image)
        self._surface = surf
        return surf


@TextureGenerator.register_subclass('random_tiles')
class RandomTilesTexture(RandomTexture):
    def __init__(
        self,
        size,
        size_tiles,
        color_min: Union[Tuple[int, int, int], List[int]],
        color_max: Union[Tuple[int, int, int], List[int]],
        rng=None,
    ):

        assert isinstance(color_min, (tuple, list))
        assert len(color_min) == 3

        assert isinstance(color_max, (tuple, list))
        assert len(color_max) == 3

        super().__init__(size, rng)

        assert size_tiles <= self._size[0] and size_tiles <= self._size[1]

        self._shape_mini = int(self._size[0] * 1.0 / size_tiles), int(
            self._size[1] * 1.0 / size_tiles), 3

        self._min = color_min
        self._max = color_max

    def generate(self):

        random_image = self._rng.uniform(self._min, self._max,
                                         self._shape_mini).astype('int')
        random_image = resize(random_image,
                              self._size,
                              order=0,
                              preserve_range=True)
        surf = surfarray.make_surface(random_image)
        self._surface = surf
        return surf


@TextureGenerator.register_subclass('centered_random_tiles')
class CenteredRandomTilesTexture(RandomTexture):
    def __init__(
        self,
        size,
        size_tiles,
        color_min: Union[Tuple[int, int, int], List[int]],
        color_max: Union[Tuple[int, int, int], List[int]],
        rng=None,
    ):

        assert isinstance(color_min, (tuple, list))
        assert len(color_min) == 3

        assert isinstance(color_max, (tuple, list))
        assert len(color_max) == 3

        super().__init__(size, rng)

        assert size_tiles <= self._size[0] and size_tiles <= self._size[1]

        self._radius = max(self._size)

        self._min = color_min
        self._max = color_max

        self.n_stripes = int(2 * math.pi * self._radius / size_tiles)

    def generate(self):

        img = np.zeros((*self._size, 3))

        colors = [[
            self._rng.integers(self._min[i], self._max[i], endpoint=True)
            for i in range(3)
        ] for _ in range(self.n_stripes)]

        x = (self._size[0] - 1) / 2
        y = (self._size[1] - 1) / 2

        for i in range(self._size[0]):
            for j in range(self._size[1]):

                angle = int(
                    np.arctan2(j - y, i - x) / (2 * math.pi / self.n_stripes))

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        self._surface = surf
        return surf


@TextureGenerator.register_subclass('list_centered_random_tiles')
class ListCenteredRandomTiles(RandomTexture):
    def __init__(
        self,
        size,
        size_tiles,
        colors: List[Union[Tuple[int, int, int], List[int]]],
        rng=None,
    ):

        super().__init__(size, rng)

        self._radius = max(self._size)

        self._n_stripes = int(2 * math.pi * self._radius / size_tiles)

        for color in colors:
            assert isinstance(color, (tuple, list))
            assert len(color) == 3

        self._colors = colors

    def generate(self):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        img = np.zeros((*self._size, 3))

        colors = self._rng.choice(self._colors,
                                  size=self._n_stripes,
                                  replace=True)

        x = (self._size[0] - 1) / 2
        y = (self._size[1] - 1) / 2

        for i in range(self._size[0]):
            for j in range(self._size[1]):

                angle = int(
                    np.arctan2(j - y, i - x) / (2 * math.pi / self._n_stripes))

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        self._surface = surf
        return surf


#
# @TextureGenerator.register_subclass('unique_random_tiles')
# class UniqueRandomTilesTexture(Texture):
#
#     def __init__(self, n_colors=10, delta_uniform=5, size_tiles=4,
#                  color_min=(0, 0, 0), color_max=(255, 255, 255), **kwargs):
#
#         super().__init__(**kwargs)
#         self.n_colors = n_colors
#         self.delta_uniform = delta_uniform
#         self.size_tiles = size_tiles
#         self.color_min = color_min
#         self.color_max = color_max
#
#         n_r_splits = n_colors #int( n_colors ** (1/3) )
#         n_g_splits = n_colors #int( n_colors ** (1/3))
#         n_b_splits = n_colors #n_colors - 2*int(n_colors ** (1/3))
#
#         r_list = [ color_min[0] + n_r * (color_max[0] - color_min[0] )/ (n_r_splits-1) for n_r in range(0, n_r_splits) ]
#         g_list = [ color_min[1] + n_g * (color_max[1] - color_min[1] ) / (n_g_splits-1) for n_g in range(0, n_g_splits) ]
#         b_list = [ color_min[2] + n_b * (color_max[2] - color_min[2] ) / (n_b_splits-1) for n_b in range(0, n_b_splits) ]
#
#         self.list_rgb_colors = []
#
#         for r in r_list:
#             for g in g_list:
#                 for b in b_list:
#                     self.list_rgb_colors.append([r,b,g])
#
#         self.rng_texture = kwargs.get('rng_texture', np.random.default_rng() )
#         self.rng_texture.shuffle(self.list_rgb_colors)
#
#     def generate(self):
#         """
#         Generate a pygame Surface with pixels following a uniform density
#         :param width: the width of the generated Surface
#         :param height: the height of the generated Surface
#         :return: the pygame Surface
#         """
#
#         color = self.list_rgb_colors.pop()
#         min_color = [ max(0, x - self.delta_uniform) for x in color]
#         max_color = [ min(255, x + self.delta_uniform) for x in color]
#
#         random_image = self.rng_texture.uniform(min_color, max_color, (int(self._size * 1.0 / self.size_tiles), int(self._size * 1.0 / self.size_tiles), 3)).astype('int')
#         random_image = resize(random_image, (self._size, self._size), order=0, preserve_range=True)
#         surf = surfarray.make_surface(random_image)
#         return surf
#
#
# @TextureGenerator.register_subclass('polar_stripes')
# class PolarStripesTexture(Texture):
#
#     def __init__(self, **params):
#         super().__init__(**params)
#         self.color_1 = params['color_1']
#         self.color_2 = params['color_2']
#         self.n_stripes = params['n_stripes']
#         self.rng_texture = params.get('rng_texture', np.random.default_rng() )
#
#
#
#     def generate(self):
#         """
#         Generate a pygame Surface with pixels following a circular striped pattern from the center of the parent entity
#         :param width: the width of the generated surface
#         :param height: the height of the generated surface
#         :return: the pygame Surface
#         """
#
#         img = np.zeros((self._size, self._size , 3))
#
#         x = (self._size - 1) / 2
#         y = (self._size - 1) / 2
#
#         for i in range(self._size):
#             for j in range(self._size):
#
#                 angle = np.arctan2( j - y, i - x)  % (2*math.pi/self.n_stripes)
#
#                 if angle > math.pi/(self.n_stripes) :
#                     img[i, j, :] = self.color_1
#                 else:
#                     img[i, j, :] = self.color_2
#
#         surf = surfarray.make_surface(img)
#         return surf
#
#
#
#

#
