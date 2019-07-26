import pymunk


class Appearance():

    subclasses = {}

    @classmethod
    def register_subclass( cls, appearance_shape):
        def decorator(subclass):
            cls.subclasses[appearance_shape] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        appearance_shape = params['appearance_shape']
        if appearance_shape not in cls.subclasses:
            raise ValueError('Appearance Shape not implemented:'+appearance_shape)

        return cls.subclasses[appearance_shape](params)


@Appearance.register_subclass('rectangle')
class Rectangle( Appearance ):

    def __init__(self, params):

        self.width, self.length = params['shape']

        self.shape = pymunk.Segment(
            body = None,
            a = (0, -self.length/2.0),
            b = (0, self.length/2.0),
            radius = self.width
        )

        self.texture_surface = self.texture.Texture.create(params)
        self.texture_surface.set_colorkey((0, 0, 0, 0))
