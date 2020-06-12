from flatland.entities.entity import Entity
import pymunk, pygame
from flatland.utils import texture
from flatland.utils.config import *
import math
from pygame.locals import *
import yaml, os
from pymunk import ShapeFilter
from ..agent import Action


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

    part_count = 1

    joint = None
    motor = None
    limit = None

    def __init__(self, **body_part_params):

        super(BodyPart, self).__init__(initial_position=[0,0,0], **body_part_params)

        self.part_number = BodyPart.part_count
        BodyPart.part_count += 1

        self.can_eat = body_part_params.get('can_eat', False)
        self.can_activate = body_part_params.get('can_activate', False)
        self.can_grasp = body_part_params.get('can_grasp', False)
        if self.can_grasp:
            self.grasped = []

        self.pm_visible_shape.collision_type = CollisionTypes.AGENT
        #self.pm_visible_shape.elasticity = 0.0
        #self.pm_visible_shape.friction = 0.0

        # self.pm_visible_shape.filter = pymunk.ShapeFilter(group=1)

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
            action = Action( self.name, ActionTypes.GRASP, ActionTypes.DISCRETE, 0, 1)#K_g, ActionTypes.PRESS_HOLD, 1)
            actions.append(action)

        if self.can_activate:
            action = Action(self.name, ActionTypes.ACTIVATE, ActionTypes.DISCRETE, 0, 1)#, K_a, ActionTypes.PRESS_RELEASE, 1)
            actions.append(action)

        if self.can_eat:
            action = Action(self.name, ActionTypes.EAT, ActionTypes.DISCRETE, 0, 1)#, K_e, ActionTypes.PRESS_RELEASE, 1)
            actions.append(action)

        return actions

    def apply_actions(self, actions):

        if self.can_activate:
            self.is_activating = actions.get(ActionTypes.ACTIVATE, False)

        if self.can_eat:
            self.is_eating = actions.get(ActionTypes.EAT, False)

        if self.can_grasp:
            self.is_grasping = actions.get(ActionTypes.GRASP, False)

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

    @property
    def part_number(self):
        return self._part_number

    @part_number.setter
    def part_number(self, part_numb):
        self._part_number = part_numb
        self.pm_visible_shape.filter = ShapeFilter(categories=self._part_number)


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

        action = Action( self.name, ActionTypes.LONGITUDINAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_UP, ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action( self.name, ActionTypes.LONGITUDINAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_DOWN, ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        action = Action(self.name, ActionTypes.LATERAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_n,
                        # ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        action = Action(self.name, ActionTypes.LATERAL_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_m,
                        # ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_LEFT,
                        # ActionTypes.PRESS_HOLD, 1)
        actions.append(action)

        action = Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)#, K_RIGHT,
                        # ActionTypes.PRESS_HOLD, -1)
        actions.append(action)

        return actions

    def create_visible_mask(self):

        mask = super().create_visible_mask()

        pygame.draw.line(mask, pygame.color.THECOLORS["blue"], (self.radius, self.radius), (self.radius, 2 * self.radius), 2)

        return mask


class Limb(BodyPart):

    def __init__(self, anchor, relative_position_of_anchor_on_anchor, relative_position_of_anchor_on_part, angle_offset, **kwargs):

        self.anchor = anchor

        super(Limb, self).__init__(**kwargs)

        self.max_angular_velocity = kwargs['max_angular_velocity']
        self.rotation_range = kwargs['rotation_range']


        self.angle_offset = angle_offset

        self.relative_position_of_anchor_on_anchor = relative_position_of_anchor_on_anchor
        self.relative_position_of_anchor_on_part = relative_position_of_anchor_on_part

        self.set_relative_position()

        x0, y0 = self.relative_position_of_anchor_on_anchor
        x0, y0 = y0, -x0

        x1, y1 = self.relative_position_of_anchor_on_part
        x1, y1 = y1, -x1

        self.joint = pymunk.PivotJoint(anchor.pm_body, self.pm_body,  (x0, y0), (x1, y1))
        self.limit = pymunk.RotaryLimitJoint(anchor.pm_body, self.pm_body,
                                        self.angle_offset - self.rotation_range/2 ,
                                        self.angle_offset + self.rotation_range/2)

        self.motor = pymunk.SimpleMotor(anchor.pm_body, self.pm_body, 0)

        #self.pm_elements += [self.joint, self.motor, self.limit]
        self.pm_elements += [self.joint, self.motor, self.limit]


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
        theta_part = (self.anchor.pm_body.angle + self.angle_offset + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_part, y_anchor_relative_of_part = self.relative_position_of_anchor_on_part

        x_anchor_coordinates_part =  x_anchor_relative_of_part * math.cos(theta_part - math.pi / 2) - \
                                      y_anchor_relative_of_part * math.sin(theta_part - math.pi / 2)
        y_anchor_coordinates_part =  x_anchor_relative_of_part * math.sin(theta_part - math.pi / 2) + \
                                      y_anchor_relative_of_part * math.cos(theta_part - math.pi / 2)

        # Move part to align on anchor
        y = -(x_anchor_coordinates_anchor - x_anchor_coordinates_part)
        x = y_anchor_coordinates_anchor - y_anchor_coordinates_part
        self.pm_body.position = ( x, y )

        # theta_part = theta_part + math.pi / 2
        # theta_part = theta_part - 2 * math.pi if theta_part > math.pi else theta_part

        self.pm_body.angle = self.anchor.pm_body.angle + self.angle_offset

    def get_available_actions(self):

        #actions = super().get_available_actions()
        actions = []

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)
        actions.append(action)

        action = Action( self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS, -1, 1)
        actions.append(action)

        return actions


    def apply_actions(self, actions):

        super().apply_actions(actions)

        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        self.motor.rate = angular_velocity * self.max_angular_velocity

        ### Case when theta close to limit -> speed to zero
        theta_part = self.position[2]
        theta_anchor = self.anchor.position[2]

        angle_centered = (theta_part - (theta_anchor+self.angle_offset))%(2*math.pi)
        angle_centered = angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered

        # Do not set the motor if the limb is close to limit
        if angle_centered < - self.rotation_range/2 + math.pi/20 and angular_velocity > 0 :
            self.motor.rate = 0

        elif angle_centered > self.rotation_range/2 - math.pi/20 and angular_velocity < 0 :
            self.motor.rate = 0

    def create_visible_mask(self):

        mask = super().create_visible_mask()
        pygame.draw.line(mask, pygame.color.THECOLORS["green"], (self.radius, self.radius), (self.radius, 2 * self.radius), 2)

        return mask

    @property
    def part_number(self):
        return self._part_number

    @part_number.setter
    def part_number(self, part_numb):

        mask = pymunk.ShapeFilter.ALL_MASKS - int(2**(self.anchor.part_number-1))
        category = 2**(part_numb-1)

        self._part_number = part_numb
        self.pm_visible_shape.filter = ShapeFilter(categories=category, mask=mask)


class Head(Limb):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self.parse_configuration('parts', 'head')
        default_config['rotation_range'] *= math.pi / 180

        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        position_part = [0,0]

        super(Head, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

    @property
    def part_number(self):
        return self._part_number

    @part_number.setter
    def part_number(self, part_numb):

        self._part_number = part_numb
        self.pm_visible_shape.filter = ShapeFilter(categories=self._part_number, mask = 0b0)


class Eye(Limb):

    def __init__(self, anchor, position_anchor, angle_offset = 0,  **kwargs):

        default_config = self.parse_configuration('parts', 'eye')
        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        position_part = [0,0]

        super(Eye, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

    @property
    def part_number(self):
        return self._part_number

    @part_number.setter
    def part_number(self, part_numb):

        self._part_number = part_numb
        self.pm_visible_shape.filter = ShapeFilter(categories=self._part_number, mask=0b0)


class Arm(Limb):

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = self.parse_configuration('parts', 'arm')
        body_part_params = {**default_config, **kwargs}

        # head attached in its center
        width, length = body_part_params['width_length']
        position_part = [0, -length/2.0 + width/2.0]

        self.extremity_anchor_point = [0, length/2.0 - width/2.0]

        super(Arm, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.motor.max_force = 500
