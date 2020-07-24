"""
Module for Texture of SceneElements and Parts of Agents.
Documentation is incomplete/missing. Refer to the tutorials for now.
"""

import math
import random
from abc import ABC, abstractmethod

import numpy as np
from pygame import Surface
from pygame import surfarray
import cv2

#pylint: disable=all

class TextureGenerator:
    """
    Class to register Textures.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, texture_type):
        """ Registers a class Texture """
        def decorator(subclass):

            cls.subclasses[texture_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        """ Create a new instance of Class Texture based on its parameters."""
        texture_type = params['texture_type']

        if texture_type not in cls.subclasses:
            raise ValueError('Texture not implemented: '+texture_type)

        return cls.subclasses[texture_type](**params)


class Texture(ABC):

    """ Base Class for Textue"""

    def __init__(self, **kwargs):

        self.size = int(kwargs.get('radius')*2 + 1)
        self.surface = Surface((self.size, self.size))
        self.radius = kwargs['radius']

    @abstractmethod
    def generate(self):

        """ Generates a pygame surface at the correct dimension"""


@TextureGenerator.register_subclass('color')
class ColorTexture(Texture):

    """ Simple Uniform texture of a single color"""

    def __init__(self, **params):
        super().__init__(**params)
        self.color = params['color']

    def generate(self):

        self.surface.fill(self.color)
        return self.surface



@TextureGenerator.register_subclass('uniform')
class UniformTexture(Texture):

    """ Random Uniform Texture."""

    def __init__(self, **params):
        super().__init__(**params)
        self.min = params['color_min']
        self.max = params['color_max']

    def generate(self):

        random_image = np.random.uniform(self.min, self.max, (self.size, self.size, 3))
        random_image = random_image.astype('int')
        surf = surfarray.make_surface(random_image)
        return surf


@TextureGenerator.register_subclass('random_tiles')
class RandomTilesTexture(Texture):

    def __init__(self, **params):
        super().__init__(**params)
        self.min = params['color_min']
        self.max = params['color_max']
        self.size_tiles = params['size_tiles']

    def generate(self):

        size_shrink = (int(self.size*1.0/self.size_tiles), int(self.size*1.0/self.size_tiles), 3)
        random_image = np.random.uniform(self.min, self.max, size_shrink).astype('int')
        random_image = cv2.resize(random_image, ( self.size, self.size ), interpolation=cv2.INTER_NEAREST)
        surf = surfarray.make_surface(random_image)
        return surf


@TextureGenerator.register_subclass('unique_random_tiles')
class UniqueRandomTilesTexture(Texture):

    def __init__(self, n_colors=10, delta_uniform=5, size_tiles=4,
                 color_min=(0, 0, 0), color_max=(255, 255, 255), **kwargs):

        super().__init__(**kwargs)
        self.n_colors = n_colors
        self.delta_uniform = delta_uniform
        self.size_tiles = size_tiles
        self.color_min = color_min
        self.color_max = color_max

        n_r_splits = n_colors #int( n_colors ** (1/3) )
        n_g_splits = n_colors #int( n_colors ** (1/3))
        n_b_splits = n_colors #n_colors - 2*int(n_colors ** (1/3))

        r_list = [ color_min[0] + n_r * (color_max[0] - color_min[0] )/ (n_r_splits-1) for n_r in range(0, n_r_splits) ]
        g_list = [ color_min[1] + n_g * (color_max[1] - color_min[1] ) / (n_g_splits-1) for n_g in range(0, n_g_splits) ]
        b_list = [ color_min[2] + n_b * (color_max[2] - color_min[2] ) / (n_b_splits-1) for n_b in range(0, n_b_splits) ]

        self.list_rgb_colors = []

        for r in r_list:
            for g in g_list:
                for b in b_list:
                    self.list_rgb_colors.append([r,b,g])

        random.shuffle(self.list_rgb_colors)

    def generate(self):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        color = self.list_rgb_colors.pop()
        min_color = [ max(0, x - self.delta_uniform) for x in color]
        max_color = [ min(255, x + self.delta_uniform) for x in color]

        random_image = np.random.uniform(min_color, max_color, (int(self.size*1.0/self.size_tiles), int(self.size*1.0/self.size_tiles), 3)).astype('int')
        random_image = cv2.resize(random_image, ( self.size, self.size ), interpolation=cv2.INTER_NEAREST)
        surf = surfarray.make_surface(random_image)
        return surf


@TextureGenerator.register_subclass('polar_stripes')
class PolarStripesTexture(Texture):

    def __init__(self, **params):
        super().__init__(**params)
        self.color_1 = params['color_1']
        self.color_2 = params['color_2']
        self.n_stripes = params['n_stripes']

    def generate(self):
        """
        Generate a pygame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        img = np.zeros( (self.size, self.size , 3) )

        x = (self.size - 1) / 2
        y = (self.size - 1) / 2

        for i in range(self.size):
            for j in range(self.size):

                angle = np.arctan2( j - y, i - x)  % (2*math.pi/self.n_stripes)

                if angle > math.pi/(self.n_stripes) :
                    img[i, j, :] = self.color_1
                else:
                    img[i, j, :] = self.color_2

        surf = surfarray.make_surface(img)
        return surf


@TextureGenerator.register_subclass('unique_polar_stripe')
class UniqueCenteredStripeTexture(Texture):

    def __init__(self, **params):
        super().__init__(**params)
        self.color = params['color']
        self.color_stripe = params['color_stripe']
        self.size_stripe = params['size_stripe']

    def generate(self):
        """
        Generate a pygame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        img = np.zeros( (self.size, self.size , 3) )
        img[:,:,:] = self.color

        x = int((self.size - 1) / 2.0)
        y = int((self.size - 1) / 2.0)

        dsize = int(self.size_stripe/2.0)

        for dx in range(x, self.size):
            for dy in range(-dsize, dsize+1):

                img[y+dy, dx, :] = self.color_stripe

        surf = surfarray.make_surface(img)
        return surf

@TextureGenerator.register_subclass('centered_random_tiles')
class CenteredRandomTilesTexture(Texture):

    def __init__(self, **params):
        super().__init__(**params)
        self.min = params['color_min']
        self.max = params['color_max']
        self.radius = params['radius']
        self.size_tiles = params['size_tiles']
        self.n_stripes = int(2*math.pi*self.radius / self.size_tiles)

    def generate(self):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        img = np.zeros( (self.size, self.size, 3) )

        colors = [ [ random.randint( self.min[i],self.max[i] ) for i in range(3)] for c in range(self.n_stripes) ]

        x = (self.size - 1) / 2
        y = (self.size - 1) / 2

        for i in range(self.size):
            for j in range(self.size):

                angle = int( np.arctan2( j - y, i - x)  / (2*math.pi/self.n_stripes) )

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        return surf


@TextureGenerator.register_subclass('list_centered_random_tiles')
class ListCenteredRandomTiles(Texture):

    def __init__(self, **params):
        super().__init__(**params)
        self.radius = params['radius']
        self.size_tiles = params['size_tiles']
        self.n_stripes = int(2*math.pi*self.radius / self.size_tiles)
        self.colors = params['colors']

    def generate(self):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        img = np.zeros( (self.size, self.size , 3) )

        colors = random.choices( self.colors, k = self.n_stripes)

        x = (self.size - 1) / 2
        y = (self.size - 1) / 2

        for i in range(self.size):
            for j in range(self.size):

                angle = int( np.arctan2( j - y, i - x)  / (2*math.pi/self.n_stripes) )

                img[i, j, :] = colors[angle]

        surf = surfarray.make_surface(img)
        return surf

