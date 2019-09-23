from pygame import Surface, PixelArray, SRCALPHA
import pygame, cv2


from scipy.stats import truncnorm
import numpy.random as rand
import numpy as np
import math

class Texture(object):

    subclasses = {}

    @classmethod
    def register_subclass(cls, texture_type):

        def decorator(subclass):

            cls.subclasses[texture_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        texture_type = params['type']

        if texture_type not in cls.subclasses:
            raise ValueError('Texture not implemented: '+texture_type)

        return cls.subclasses[texture_type](**params)


@Texture.register_subclass('color')
class ColorTexture(Texture):

    def __init__(self, **params):
        super(ColorTexture, self).__init__()
        self.color = params['color']

    def generate(self, width, height):
        surface = Surface((width, height))
        surface.fill(self.color)
        return surface



@Texture.register_subclass('uniform')
class UniformTexture(Texture):

    def __init__(self, **params):
        super(UniformTexture, self).__init__()
        self.min = params['min']
        self.max = params['max']

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        random_image = np.random.uniform(self.min, self.max, (int(width), int(height), 3)).astype('int')
        print(random_image.shape)
        surf = pygame.surfarray.make_surface(random_image)
        return surf


@Texture.register_subclass('uniform_grained')
class UniformGrainedTexture(Texture):

    def __init__(self, **params):
        super(UniformGrainedTexture, self).__init__()
        self.min = params['min']
        self.max = params['max']
        self.size_grains = params['size_grains']

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a uniform density
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        random_image = np.random.uniform(self.min, self.max, (int(width*1.0/self.size_grains), int(height*1.0/self.size_grains), 3)).astype('int')
        random_image = cv2.resize(random_image, ( int(height), int(width) ), interpolation=cv2.INTER_NEAREST)
        surf = pygame.surfarray.make_surface(random_image)
        return surf

@Texture.register_subclass('polar_stripes')
class PolarStripesTexture(Texture):

    def __init__(self, **params):
        super(PolarStripesTexture, self).__init__()
        self.color_1 = params['color_1']
        self.color_2 = params['color_2']
        self.n_stripes = params['n_stripes']

    def generate(self, width, height):
        """
        Generate a pyame Surface with pixels following a circular striped pattern from the center of the parent entity
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        width = int(width)
        height = int(height)

        img = np.zeros( (width, height , 3) )

        x = width/2
        y = height/2

        for i in range(width):
            for j in range(height):

                angle = np.arctan2( j - y, i - x)  % (2*math.pi/self.n_stripes)

                if angle  > math.pi/(self.n_stripes) :
                    img[i, j, :] = self.color_1
                else:
                    img[i, j, :] = self.color_2

        surf = pygame.surfarray.make_surface(img)
        return surf


class NormalTexture(Texture):

    def __init__(self, m, d):
        super(NormalTexture, self).__init__()
        self.m = m
        self.d = d

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a normal density of diagonal covariance matrix.
        :param width: the width of the generated Surface
        :param height: the height of the generated Surface
        :return: the pygame Surface
        """

        surface = Surface((width, height), SRCALPHA)
        pxarray = PixelArray(surface)

        m = np.array(self.m)
        d = np.array(self.d)

        t = np.zeros((width, height, 3))

        for c in range(3):
            a, b = (0 - m[c]) / d[c], (255 - m[c])/d[c]
            tc = truncnorm.rvs(a, b, size=width * height)
            t[:, :, c] = tc.reshape(width, height)

        for i in range(width):
            for j in range(height):
                pxarray[i, j] = tuple((d * t[i, j] + m).astype(int))

        return surface


class StripesTexture(Texture):

    def __init__(self, colors, lengths, angle):
        super(StripesTexture, self).__init__()
        self.colors = colors
        self.lengths = lengths
        self.angle = angle
        assert len(self.colors) == len(self.lengths), "Parameters 'lengths' and 'colors' should be the same length."

    def generate(self, width, height):
        """
        Generate a pygame Surface with pixels following a striped pattern.
        :param width: the width of the generated surface
        :param height: the height of the generated surface
        :return: the pygame Surface
        """

        surface = Surface((width, height), SRCALPHA)
        pxarray = PixelArray(surface)

        for i in range(width):
            for j in range(height):
                l = np.sqrt(i**2 + j**2) * np.cos(np.arctan((j+1)/(i+1)) - self.angle)
                r = l % sum(self.lengths)
                for mode, d in enumerate(np.cumsum(self.lengths)):
                    if r < d:
                        pxarray[i, j] = self.colors[mode]
                        break

        return surface



