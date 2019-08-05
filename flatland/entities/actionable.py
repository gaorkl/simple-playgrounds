import pymunk, random, pygame

from .basic import  BasicObject
from flatland.utils.config import *


class ActionableObject(BasicObject):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """
        super(ActionableObject, self).__init__(params)

        self.default_texture = {
            'type': 'color',
            'color': (10, 30, 200)
        }

        self.action_radius = params['action_radius']
        self.actionable_type = params['actionable_type']

        self.params = params

        self.name_id = self.actionable_type + '_'+str(EdibleObject.id_number)

        shape_sensor = self.generate_pymunk_sensor_shape( self.body_body )

        if 'default_color' in params:
            self.shape_body.color = params['default_color']

        self.shape_sensor = shape_sensor

        self.body_sensor = self.body_body.copy()

        self.shape_body.collision_type = collision_types['basic_object']


    def actionate(self):

        print('Is actionated')


    def generate_pymunk_sensor_shape(self, body):


        if self.physical_shape == 'circle':

            shape_sensor = pymunk.Circle(body, self.radius + self.action_radius)

            shape_sensor.sensor = True

        #TODO : activables with other shapes
        #elif self.physical_shape == 'poly':

        #    shape = pymunk.Poly(body, self.vertices)

        #elif self.physical_shape == 'box':

        #    shape = pymunk.Poly.create_box(body, self.size_box)

        else:

            raise ValueError('Not implemented')

        return shape_sensor



    def compute_moments(self):

        if self.physical_shape == 'circle':

            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape == 'poly':

            moment = pymunk.moment_for_poly(self.mass, self.vertices)

        elif self.physical_shape == 'box':

            moment =  pymunk.moment_for_box(self.mass, self.size_box)

        else:

            raise ValueError('Not implemented')

        return moment


    def draw(self, surface, with_action_radius = True):
        """
        Draw the obstacle on the environment screen
        """

        radius = int(self.radius) + self.action_radius

        # Create a texture surface with the right dimensions
        if self.texture_surface is None:
            self.texture_surface = self.texture.generate(radius * 2, radius * 2)

        # Create the mask
        mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        pygame.draw.circle(mask, (255, 255, 255, 50), (radius, radius), radius)

        # Apply texture on mask
        mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
        mask_rect = mask.get_rect()
        mask_rect.center = self.body_body.position[1], self.body_body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)

        super().draw(surface)


    #
    #     if self.appearance == 'rectangle':
    #
    #         # Rotate and center the texture
    #
    #         texture_surface = pygame.transform.rotate(self.texture, self.theta * 180/math.pi)
    #         texture_surface_rect = texture_surface.get_rect()
    #         texture_surface_rect.center = pygame_utils.to_pygame((self.x, self.y), surface)
    #
    #         # Blit the masked texture on the screen
    #         surface.blit(texture_surface, texture_surface_rect, None)



class ActionableGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, actionable_type):
        def decorator(subclass):
            cls.subclasses[actionable_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        actionable_type = params['actionable_type']
        if actionable_type not in cls.subclasses:
            #TODO: verify rais eerroe?
            raise ValueError('Entity type not implemented:' + actionable_type)

        return cls.subclasses[actionable_type](params)


@ActionableGenerator.register_subclass('distractor')
class DistractorObject(ActionableObject):

    def __init__(self, params):

        super(DistractorObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']


    def actionate(self):

        self.shape_body.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


@ActionableGenerator.register_subclass('edible')
class EdibleObject(ActionableObject):

    def __init__(self, params):

        super(EdibleObject, self).__init__(params)

        self.shrink_when_eaten = params['shrink_when_eaten']

        self.shape_sensor.collision_type = collision_types['edible']

        self.reward = params.get('initial_reward', 0)



    def actionate(self):

        #self.radius = self.shrink_when_eaten * self.radius
        #self.reward = self.shrink_when_eaten * self.reward

        #
        # if self.movable:
        #     self.mass = self.shrink_when_eaten * self.mass
        #     inertia = self.compute_moments()
        #     body = pymunk.Body(self.mass, inertia)
        #
        # else:
        #     self.mass = None
        #     body = pymunk.Body(body_type=pymunk.Body.STATIC)
        #
        # body.position = self.body_body.position
        # body.angle = self.body_body.angle
        #
        # self.body_body = body
        # shape_sensor = self.generate_pymunk_sensor_shape( self.body_body )
        #
        # self.shape_body = shape_body
        # self.shape_body.friction = 1.
        # self.shape_body.elasticity = 0.95
        #
        #
        # if 'default_color' in self.params:
        #     self.shape_body.color = self.params['default_color']
        # #
        # self.shape_sensor = shape_sensor
        #
        # self.shape_sensor.collision_type = collision_types['edible']
        # #
        # self.body_sensor = self.body_body.copy()
        #

        # TODO: dirty, very dirty. Should be replaced
        self.params['radius'] = self.shrink_when_eaten * self.radius
        self.params['reward'] = self.shrink_when_eaten * self.reward

        # TODO: harmonize angles and positions x,y,theta ... body.position, body.angle ...
        self.params['position'] = ( self.body_body.position[0], self.body_body.position[1], self.body_body.angle)

        self.__init__(self.params)
        self.initialize_texture()


@ActionableGenerator.register_subclass('dispenser')
class DispenserObject(ActionableObject):

    def __init__(self, params):

        super(DispenserObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']

        self.object_produced = params['object']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.limit = params['limit']


    def actionate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj

@ActionableGenerator.register_subclass('graspable')
class GraspableObject(ActionableObject):

    def __init__(self, params):

        super(GraspableObject, self).__init__( params)

        self.shape_sensor.collision_type = collision_types['graspable']

        self.graspable = True

    def actionate(self):
        pass



@ActionableGenerator.register_subclass('door')
class DoorObject(ActionableObject):

    def __init__(self, params):

        super(DoorObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']

        self.door_params = params['door']

        self.time_open = params['time_open']

        self.door_closed = True

    def actionate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj


