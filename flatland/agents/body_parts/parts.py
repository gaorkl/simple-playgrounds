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


shape_filter = pymunk.ShapeFilter(group=1)

def polar_to_carthesian(coord):

    r, phi = coord

    x = r*math.cos(phi)
    y = r*math.sin(phi)

    return x,y



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


        self.can_eat = body_part_params.get('can_eat', False)
        self.can_activate = body_part_params.get('can_activate', False)
        self.can_grasp = body_part_params.get('can_grasp', False)
        if self.can_grasp:
            self.grasped = []

        self.pm_visible_shape.collision_type = CollisionTypes.AGENT
        self.pm_visible_shape.filter = shape_filter

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

    def get_available_actions(self):

        actions = []

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

    def apply_actions(self, actions):

        if self.can_activate: self.is_activating = actions.get(ActionTypes.ACTIVATE, False)

        if self.can_eat: self.is_eating = actions.get(ActionTypes.EAT, False)

        if self.can_grasp: self.is_grasping = actions.get(ActionTypes.GRASP, False)
        if self.is_holding and not self.is_grasping: self.is_holding = False


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


class CircularPan(BodyPart):

    def __init__(self, anchor, relative_position_of_anchor_on_anchor, relative_position_of_anchor_on_part, angle_offset, **kwargs):

        super(CircularPan, self).__init__(**kwargs)

        self.max_angular_velocity = kwargs['max_angular_velocity']
        self.rotation_range = kwargs['rotation_range']*math.pi/180

        # Avoid collision with own body:
        # self.pm_visible_shape.sensor = True

        self.anchor = anchor
        self.angle_offset = angle_offset

        self.relative_position_of_anchor_on_anchor = relative_position_of_anchor_on_anchor
        self.relative_position_of_anchor_on_part = relative_position_of_anchor_on_part

        self.set_relative_position()

        x0, y0 = self.relative_position_of_anchor_on_anchor
        x0, y0 = y0, -x0

        x1, y1 = self.relative_position_of_anchor_on_part
        x1, y1 = y1, -x1

        print('--------------')
        print(anchor.pm_body.angle, self.pm_body.angle)
        print(self.rotation_range/2)

        joint = pymunk.PivotJoint(anchor.pm_body, self.pm_body,  (x0, y0), (x1, y1))
        limit = pymunk.RotaryLimitJoint(anchor.pm_body, self.pm_body, self.angle_offset - self.rotation_range/2 , self.angle_offset + self.rotation_range/2)

        self.motor = pymunk.SimpleMotor(anchor.pm_body, self.pm_body, 0)


        # self.pm_elements += [joint, self.motor]
        self.pm_elements += [joint, self.motor, limit]

    def set_relative_position(self):

        # Get position of the anchor point on anchor
        x_anchor_center, y_anchor_center = self.anchor.pm_body.position
        x_anchor_center, y_anchor_center = -y_anchor_center, x_anchor_center
        theta_anchor = (self.anchor.pm_body.angle + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_anchor, y_anchor_relative_of_anchor = self.relative_position_of_anchor_on_anchor

        x_anchor_coordinates_anchor = x_anchor_center + x_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2 ) -\
                                      y_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2 )
        y_anchor_coordinates_anchor = y_anchor_center + x_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2 ) + \
                                      y_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2 )

        # Get position of the anchor point on part
        #x_part_center, y_part_center = self.pm_body.position
        #x_part_center, y_part_center = -y_part_center, x_part_center
        theta_part = (self.anchor.pm_body.angle + self.angle_offset + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_part, y_anchor_relative_of_part = self.relative_position_of_anchor_on_part

        x_anchor_coordinates_part =  x_anchor_relative_of_part * math.cos(theta_part - math.pi / 2) - \
                                      y_anchor_relative_of_part * math.sin(theta_part - math.pi / 2)
        y_anchor_coordinates_part =  x_anchor_relative_of_part * math.sin(theta_part - math.pi / 2) + \
                                      y_anchor_relative_of_part * math.cos(theta_part - math.pi / 2)

        # Move part to align on anchor

        y = -(x_anchor_coordinates_anchor + x_anchor_coordinates_part)
        x = y_anchor_coordinates_anchor + y_anchor_coordinates_part

        #print(y, x)

        self.pm_body.position = ( x, y )

        self.pm_body.angle = theta_part - math.pi / 2

        return x, y
    #
    #
    # @property
    # def relative_angle(self):
    #
    #     theta_anchor = self.anchor.position[2]
    #     theta_part = self.position[2]
    #
    #     rel_head = (theta_part-theta_anchor) % (2 * math.pi)
    #     rel_head = rel_head - 2 * math.pi if rel_head > math.pi else rel_head
    #
    #     return rel_head
    #
    # @relative_angle.setter
    # def relative_angle(self, d_theta):
    #
    #     x, y, _  = self.position
    #     theta_anchor = self.anchor.position[2]
    #
    #     d_theta_centered = (d_theta - self.angle_offset)%(2*math.pi)
    #     d_theta_centered = d_theta_centered - 2 * math.pi if d_theta_centered > math.pi else d_theta_centered
    #
    #     if d_theta_centered < - self.rotation_range/2 :
    #         d_theta = - self.rotation_range/2 + self.angle_offset
    #
    #     elif d_theta_centered > self.rotation_range/2 :
    #         d_theta =  self.rotation_range/2 + self.angle_offset
    #
    #
    #     self.position = x, y, theta_anchor + d_theta
    #

    # @property
    # def relative_position(self):
    #
    #     r, phi = self.polar_position_anchor
    #
    #     x_anchor, y_anchor = self.anchor.position
    #
    #     x, y = polar_to_carthesian([r, phi + theta_anchor, 0])
    #
    #     return x_anchor + x, y_anchor + y, theta_anchor + self.relative_angle

    def get_available_actions(self):

        #actions = super().get_available_actions()
        actions = []

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_h, ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_j, ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        return actions


    def apply_actions(self, actions):

        super().apply_actions(actions)

        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        self.motor.rate = angular_velocity * self.max_angular_velocity
        # new_angle = self.position[2] + angular_velocity * self.max_angular_velocity

        # theta_anchor = self.anchor.position[2]
        #
        # new_angle_centered = (new_angle - (theta_anchor+self.angle_offset))%(2*math.pi)
        # new_angle_centered = new_angle_centered - 2 * math.pi if new_angle_centered > math.pi else new_angle_centered
        #
        # if new_angle_centered < - self.rotation_range/2 :
        #     new_angle = - self.rotation_range/2 + self.angle_offset + theta_anchor
        #
        # elif new_angle_centered > self.rotation_range/2 :
        #     new_angle = self.rotation_range/2 + self.angle_offset + theta_anchor
        #
        # self.pm_body.angle = new_angle - math.pi/2


        # self.pm_body.angular_velocity = self.anchor.pm_body.angular_velocity + angular_velocity * self.max_angular_velocity
        #
        # angle_centered = (self.position[2] - (theta_anchor + self.angle_offset)) % (2 * math.pi)
        # angle_centered = angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered
        #
        # if angle_centered < - self.rotation_range/2 :
        #     self.pm_body.angle = - self.rotation_range/2 + self.angle_offset + theta_anchor - math.pi / 2
        #
        # elif angle_centered > self.rotation_range/2 :
        #     self.pm_body.angle = self.rotation_range/2 + self.angle_offset + theta_anchor - math.pi / 2
        #

    def create_visible_mask(self):

        mask = super().create_visible_mask()
        pygame.draw.line(mask, pygame.color.THECOLORS["green"], (self.radius, self.radius), (self.radius, 2 * self.radius), 2)

        return mask


class Head(CircularPan):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self.parse_configuration('parts', 'head')
        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        polar_position_part = [0,0]

        super(Head, self).__init__(anchor, position_anchor, polar_position_part, angle_offset, **body_part_params)

class Eye(CircularPan):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self.parse_configuration('parts', 'head')
        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        polar_position_part = [0,0]

        super(Eye, self).__init__(anchor, position_anchor, polar_position_part, angle_offset, **body_part_params)

    def get_available_actions(self):

        actions = []

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_k, ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1, K_l, ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        return actions


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
