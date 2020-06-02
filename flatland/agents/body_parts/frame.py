from flatland.entities.entity import Entity
import pymunk, pygame
from flatland.utils import texture
from flatland.utils.config import *
import math
from pygame.locals import *
import yaml, os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'frame_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


class FrameGenerator:

    """
    Register class to provide a decorator that is used to go through the package and
    register available scene_layouts.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, body_type):
        def decorator(subclass):
            cls.subclasses[body_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, body_type, params):


        if body_type not in cls.subclasses:
            raise ValueError('Body not implemented: ' + body_type)

        return cls.subclasses[body_type](params)


class BodyPart(Entity):

    """ Base Class for body parts

    Attributes:
        position
        velocity
        anchor

    Copy from Entity?

    """

    can_interact = False
    can_grasp = False


    def __init__(self, initial_position = None, anchor=None, anchor_relative_position=None, **body_part_params ):

        self.can_grasp = body_part_params.get('can_grasp', self.can_grasp)
        self.can_interact = body_part_params.get('can_interact', self.can_interact)

        self.physical_shape, self.mass, visible_size, _ = self.get_physical_properties(body_part_params)
        self.length, self.width, self.radius = visible_size

        self.visible_vertices = self.compute_vertices(self.radius)

        self.pm_body = self.create_pm_body()
        self.pm_elements = [self.pm_body]

        self.texture_params = body_part_params['texture']
        self.texture_surface = self.create_texture(self.texture_params)

        self.pm_visible_shape = self.create_pm_visible_shape()
        self.visible_mask = self.create_visible_mask()
        self.pm_elements.append(self.pm_visible_shape)


        # To be set when entity is added to playground. Used to calculate correct coordinates
        self.size_playground = None

        # To remove temporary entities when reset
        self.is_temporary_entity = body_part_params.get('is_temporary_entity', False)

    def get_available_actions(self):

        pass




class FrameParts:

    def __init__(self):

        self.body = None
        self.shapes = None
        self.joint = None


class Frame(Entity):

    def __init__(self, custom_params):

        super(Frame, self).__init__()


        self.collision_type = CollisionTypes.AGENT


        # Base
        if custom_params is not None:
            base_params = custom_params.get('base', {})
        else:
            base_params = {}

        self.base_params = {**default_config['base'], **base_params }
        self.base_translation_speed = self.base_params['translation_speed']
        self.base_rotation_speed = self.base_params['rotation_speed']
        self.base_radius = self.base_params.get("radius")
        self.base_mass = self.base_params.get("mass")

        base = FrameParts()
        inertia = pymunk.moment_for_circle(self.base_mass, 0, self.base_radius, (0, 0))
        body = pymunk.Body(self.base_mass, inertia)
        base.body = body

        shape = pymunk.Circle(body, self.base_radius, (0, 0))
        shape.elasticity = 0.5
        shape.collision_type = self.collision_type

        base.shape = shape

        self.anatomy = {"base": base}

        self.base_texture = self.base_params['texture']
        self.texture = texture.Texture.create(self.base_texture)
        self.initialize_texture()

        self.actions = {}

    def apply_actions(self, action_commands):

        self.actions = action_commands

    def initialize_texture(self):

        radius = int(self.base_radius)

        # Create a texture surface with the right dimensions
        self.texture_surface = self.texture.generate(radius * 2, radius * 2)
        self.mask =  pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.mask.fill((0, 0, 0, 0))
        pygame.draw.circle(self.mask, (255, 255, 255, 255), (radius, radius), radius)

        # Apply texture on mask
        self.mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
        pygame.draw.line(self.mask,  pygame.color.THECOLORS["blue"] , (radius,radius), (radius, 2*radius), 2)

    def draw(self, surface, visible_to_self=False):
        """
        Draw the agent on the environment screen
        """
        # Body
        if not visible_to_self:
            #print('here')
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
