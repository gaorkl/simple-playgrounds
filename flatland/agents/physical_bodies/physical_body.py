from ...entities.entity import Entity
import pymunk, pygame
from flatland.utils import texture



class BodyGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available scenes.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, body_type):
        def decorator(subclass):
            cls.subclasses[body_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):

        body_type = params.get('type', None)

        if body_type is None:
            raise ValueError('Body not selected')

        if body_type not in cls.subclasses:
            raise ValueError('Body not implemented: ' + body_type)

        return cls.subclasses[body_type](params)


class BodyParts():

    def __init__(self):

        self.body = None
        self.shapes = None
        self.joint = None


class PhysicalBody(Entity):

    def __init__(self, body_params):

        super(PhysicalBody, self).__init__()

        self.base_translation_speed = body_params['base_translation_speed']
        self.base_rotation_speed = body_params['base_rotation_speed']

        # Define the radius
        self.base_radius = body_params.get("base_radius")
        self.base_mass = body_params.get("base_mass")


        base = BodyParts()

        inertia = pymunk.moment_for_circle(self.base_mass, 0, self.base_radius, (0, 0))

        body = pymunk.Body(self.base_mass, inertia)
        base.body = body

        shape = pymunk.Circle(body, self.base_radius, (0, 0))
        shape.elasticity = 0.1
        shape.collision_type = 1

        base.shape = shape

        self.anatomy = {"base": base}

        self.base_texture = body_params['base_texture']
        self.texture = texture.Texture.create(self.base_texture)
        self.initialize_texture()


    def initialize_texture(self):

        # Trick to compute sensors without overlapping when converting to logpolar
        radius = int(self.base_radius) - 3

        # Create a texture surface with the right dimensions
        self.texture_surface = self.texture.generate(radius * 2, radius * 2)
        self.mask =  pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.mask.fill((0, 0, 0, 0))
        pygame.draw.circle(self.mask, (255, 255, 255, 255), (radius, radius), radius)

        # Apply texture on mask
        self.mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
        pygame.draw.line(self.mask,  pygame.color.THECOLORS["blue"] , (radius,radius), (radius, 2*radius), 2)

