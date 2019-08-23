from ...entities.entity import Entity
import pymunk, pygame
from flatland.utils import texture
from flatland.utils.config import *
import math
from pygame.locals import *

class FrameGenerator:

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

        return cls.subclasses[body_type](params['params'])


class FrameParts:

    def __init__(self):

        self.body = None
        self.shapes = None
        self.joint = None


class Frame(Entity):

    def __init__(self, body_params):

        super(Frame, self).__init__()

        self.base_translation_speed = body_params['base_translation_speed']
        self.base_rotation_speed = body_params['base_rotation_speed']

        # Define the radius
        self.base_radius = body_params.get("base_radius")
        self.base_mass = body_params.get("base_mass")

        self.collision_type = collision_types['agent']

        base = FrameParts()

        inertia = pymunk.moment_for_circle(self.base_mass, 0, self.base_radius, (0, 0))

        body = pymunk.Body(self.base_mass, inertia)
        base.body = body

        shape = pymunk.Circle(body, self.base_radius, (0, 0))
        shape.elasticity = 0.1
        shape.collision_type = self.collision_type

        base.shape = shape

        self.anatomy = {"base": base}

        self.base_texture = body_params['base_texture']
        self.texture = texture.Texture.create(self.base_texture)
        self.initialize_texture()

        self.actions = {}

    def apply_actions(self, action_commands):

        self.actions = action_commands

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

    def draw(self, surface):
        """
        Draw the agent on the environment screen
        """
        # Body

        mask_rotated = pygame.transform.rotate(self.mask, self.anatomy['base'].body.angle * 180 / math.pi)
        mask_rect = mask_rotated.get_rect()
        mask_rect.center = self.anatomy['base'].body.position[1], self.anatomy['base'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask_rotated, mask_rect, None)

    def get_default_key_mapping(self):
        mapping = {
            K_g: ['press_hold', 'grasp', 1],
            K_a: ['press_once', 'activate', 1],
            K_e: ['press_once', 'eat', 1]

        }

        return mapping

    def get_available_actions(self):

        actions = {
            'grasp': [0, 1, 'discrete'],
            'activate': [0, 1, 'discrete'],
            'eat': [0, 1, 'discrete'],
        }

        return actions
