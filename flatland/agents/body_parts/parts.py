from flatland.entities.entity import Entity
import pymunk, pygame
from flatland.utils import texture
from flatland.utils.config import *
import math
from pygame.locals import *
import yaml, os
from collections import namedtuple

Action = namedtuple('Action', 'body_part action action_type min max\
                              key key_behavior key_value')

class BodyPart(Entity):
    """ Base Class for body parts

    Attributes:
        position
        velocity
        anchor

    Copy from Entity?

    """

    can_grasp = False
    can_activate = False
    can_eat = False

    visible = True
    interactive = False
    movable = True

    entity_type = 'part'

    def __init__(self, **body_part_params):

        super(BodyPart, self).__init__(initial_position=[0,0,0], **body_part_params)

        # self.physical_shape, self.mass, visible_size, _ = self.get_physical_properties(body_part_params)
        # self.length, self.width, self.radius = visible_size
        #
        # self.visible_vertices = self.compute_vertices(self.radius)
        #
        # self.pm_body = self.create_pm_body()
        # self.pm_elements = [self.pm_body]
        #
        # self.texture_params = body_part_params['texture']
        # self.texture_surface = self.create_texture(self.texture_params)
        #
        # self.pm_visible_shape = self.create_pm_visible_shape()
        # self.visible_mask = self.create_visible_mask()
        # self.pm_elements.append(self.pm_visible_shape)

        self.can_eat = body_part_params.get('can_eat', False)
        self.can_activate = body_part_params.get('can_activate', False)
        self.can_grasp = body_part_params.get('can_grasp', False)
        if self.can_grasp:
            self.grasped = []

        self.pm_visible_shape.collision_type = CollisionTypes.AGENT

        self.is_eating = False
        self.is_activating = False
        self.is_grasping = False
        self.is_holding = False

        # To be set when entity is added to playground. Used to calculate correct coordinates
        self.size_playground = None

    @staticmethod
    def parse_configuration(entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]


    def apply_actions(self, actions):


        if self.can_activate:
            self.is_activating = actions.get(ActionTypes.ACTIVATE, False)

        if self.can_eat:
            self.is_eating = actions.get(ActionTypes.EAT, False)

        if self.can_grasp:
            self.is_grasping = actions.get(ActionTypes.GRASP, False)

        if self.is_holding and not self.is_grasping:
            self.is_holding = False


    def get_available_actions(self):

        actions = []
        # 'action_name boy_part_name action_type min max\
        #                               default_key default_key_behavior default_key_value')
        #

        if self.can_grasp:
            action = Action( self.name, ActionTypes.GRASP, ActionTypes.DISCRETE, 0, 1, K_g, ActionTypes.PRESS_HOLD, 1)
            actions.append(action)

        if self.can_activate:
            action = Action(self.name, ActionTypes.ACTIVATE, ActionTypes.DISCRETE, 0, 1, K_a, ActionTypes.PRESS_RELEASE, 1)
            actions.append(action)

        if self.can_eat:
            action = Action(self.name, ActionTypes.EAT, ActionTypes.DISCRETE, 0, 1, K_e, ActionTypes.PRESS_RELEASE, 1)
            actions.append(action)

        return actions



class BodyBase(BodyPart):

    def __init__(self, **kwargs):
        default_config = self.parse_configuration('parts', 'base')
        body_part_params = {**default_config, **kwargs}

        super(BodyBase, self).__init__( **body_part_params)

        self.max_linear_velocity = body_part_params['max_linear_velocity']
        self.max_angular_velocity = body_part_params['max_angular_velocity']

        self.name = 'base'

    def apply_actions(self, actions):
        """ Method to move the base of the agent.

        Args:
            longitudinal_velocity (:obj:'float'): relative value of the longitudinal velocity (in [-1, 1])
            lateral_velocity (:obj:'float'): relative value of the lateral velocity (in [-1, 1])
            angular_velocity (:obj:'float'): relative value of the angulat velocity (in [-1, 1])

        Returns:

        """

        super().apply_actions(actions)

        longitudinal_velocity = actions.get(ActionTypes.LONGITUDINAL_VELOCITY, 0)
        lateral_velocity = actions.get(ActionTypes.LATERAL_VELOCITY, 0)
        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        # TODO: Check this, SIMULATION STEPS should disappear.
        vx = longitudinal_velocity * SIMULATION_STEPS
        vy = lateral_velocity * SIMULATION_STEPS
        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(vx, vy) * self.max_linear_velocity * (1.0 - SPACE_DAMPING) * 100, (0, 0))
        self.pm_body.angular_velocity = angular_velocity * self.max_angular_velocity

    def get_available_actions(self):

        actions = super().get_available_actions()

        action = Action( self.name, ActionTypes.LONGITUDINAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_UP, ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action( self.name, ActionTypes.LONGITUDINAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_DOWN, ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        action = Action(self.name, ActionTypes.LATERAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_n,
                        ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        action = Action(self.name, ActionTypes.LATERAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_m,
                        ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_LEFT,
                        ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_RIGHT,
                        ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        return actions

    def create_visible_mask(self):

        mask = super().create_visible_mask()

        pygame.draw.line(mask, pygame.color.THECOLORS["blue"], (self.radius, self.radius), (self.radius, 2 * self.radius), 2)

        return mask

# class Head(BodyPart):
#
#     def __init__(self, initial_position, **kwargs):
#
#         default_config = self.parse_configuration('body_parts', 'head')
#         body_part_params = {**default_config, **kwargs}
#
#         super(Head, self).__init__(initial_position=initial_position, **body_part_params)
#
#         self.max_linear_velocity = body_part_params['max_linear_velocity']
#         self.max_angular_velocity = body_part_params['max_angular_velocity']
#
#     def move(self, longitudinal_velocity=0, lateral_velocity=0, angular_velocity=0):
#         """ Method to move the base of the agent.
#
#         Args:
#             longitudinal_velocity (:obj:'float'): relative value of the longitudinal velocity (in [-1, 1])
#             lateral_velocity (:obj:'float'): relative value of the lateral velocity (in [-1, 1])
#             angular_velocity (:obj:'float'): relative value of the angulat velocity (in [-1, 1])
#
#         Returns: Energy spent, depends on metabolism
#
#         """
#
#         #TODO: Check this, SIMULATION STEPS should disappear.
#         vx = longitudinal_velocity*SIMULATION_STEPS
#         vy = lateral_velocity*SIMULATION_STEPS
#         self.pm_body.apply_force_at_local_point(pymunk.Vec2d(vx, vy) * self.max_linear_velocity * (1.0 - SPACE_DAMPING) * 100, (0, 0))
#         self.pm_body.angular_velocity = angular_velocity * self.max_angular_velocity
#
#         #Can be modified to account for different metabolic models
#         energy = longitudinal_velocity + lateral_velocity + angular_velocity
#
#         return energy
#
#     def get_available_actions(self):
#
#         actions = super().get_available_actions()
#
#         actions['longitudinal_velocity'] = [-1, 1, 'continuous']
#         actions['lateral_velocity'] = [-1, 1, 'continuous']
#         actions['angular_velocity'] = [-1, 1, 'continuous']
#
#         return actions


#
#
#
#
# class FrameParts:
#
#     def __init__(self):
#
#         self.body = None
#         self.shapes = None
#         self.joint = None
#
#
# class Frame(Entity):
#
#     def __init__(self, custom_params):
#
#         super(Frame, self).__init__()
#
#
#         self.collision_type = CollisionTypes.AGENT
#
#
#         # Base
#         if custom_params is not None:
#             base_params = custom_params.get('base', {})
#         else:
#             base_params = {}
#
#         self.base_params = {**default_config['base'], **base_params }
#         self.base_translation_speed = self.base_params['translation_speed']
#         self.base_rotation_speed = self.base_params['rotation_speed']
#         self.base_radius = self.base_params.get("radius")
#         self.base_mass = self.base_params.get("mass")
#
#         base = FrameParts()
#         inertia = pymunk.moment_for_circle(self.base_mass, 0, self.base_radius, (0, 0))
#         body = pymunk.Body(self.base_mass, inertia)
#         base.body = body
#
#         shape = pymunk.Circle(body, self.base_radius, (0, 0))
#         shape.elasticity = 0.5
#         shape.collision_type = self.collision_type
#
#         base.shape = shape
#
#         self.anatomy = {"base": base}
#
#         self.base_texture = self.base_params['texture']
#         self.texture = texture.Texture.create(self.base_texture)
#         self.initialize_texture()
#
#         self.actions = {}
#
#     def apply_actions(self, action_commands):
#
#         self.actions = action_commands
#
#     def initialize_texture(self):
#
#         radius = int(self.base_radius)
#
#         # Create a texture surface with the right dimensions
#         self.texture_surface = self.texture.generate(radius * 2, radius * 2)
#         self.mask =  pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
#         self.mask.fill((0, 0, 0, 0))
#         pygame.draw.circle(self.mask, (255, 255, 255, 255), (radius, radius), radius)
#
#         # Apply texture on mask
#         self.mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
#         pygame.draw.line(self.mask,  pygame.color.THECOLORS["blue"] , (radius,radius), (radius, 2*radius), 2)
#
#     def draw(self, surface, visible_to_self=False):
#         """
#         Draw the agent on the environment screen
#         """
#         # Body
#         if not visible_to_self:
#             #print('here')
#             mask_rotated = pygame.transform.rotate(self.mask, self.anatomy['base'].body.angle * 180 / math.pi)
#             mask_rect = mask_rotated.get_rect()
#             mask_rect.center = self.anatomy['base'].body.position[1], self.anatomy['base'].body.position[0]
#
#             # Blit the masked texture on the screen
#             surface.blit(mask_rotated, mask_rect, None)
#
#     def get_default_key_mapping(self):
#         mapping = {
#             K_g: ['press_hold', 'grasp', 1],
#             K_a: ['press_once', 'activate', 1],
#             K_e: ['press_once', 'eat', 1]
#
#         }
#
#         return mapping
#
#     def get_available_actions(self):
#
#         actions = {
#             'grasp': [0, 1, 'discrete'],
#             'activate': [0, 1, 'discrete'],
#             'eat': [0, 1, 'discrete'],
#         }
#
#         return actions
