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

        # self.default_texture = {
        #     'type': 'color',
        #     'color': (10, 30, 200)
        # }

        self.activable = True
        self.action_radius = params['action_radius']
        self.actionable_type = params['actionable_type']

        self.params = params

        self.name_id = self.actionable_type + '_'+str(EdibleObject.id_number)

        shape_sensor = self.generate_pymunk_sensor_shape( self.pm_body )

        #if 'default_color' in params:
        #    self.pm_shape.color = params['default_color']

        self.pm_sensor = shape_sensor

        self.pm_shape.collision_type = collision_types['basic_object']

        self.action_radius_texture = None


    def actionate(self):

        print('Is actionated')


    def generate_pymunk_sensor_shape(self, body):

        shape_sensor = pymunk.Circle(body, self.radius + self.action_radius)

        shape_sensor.sensor = True


        return shape_sensor



    def draw(self, surface):
        """
        Draw the obstacle on the environment screen
        """
        super().draw(surface)


    def draw_activation_radius(self, surface):

        radius = int(self.radius) + self.action_radius

        # Create a texture surface with the right dimensions
        if self.action_radius_texture is None:
            self.action_radius_texture = self.texture.generate(radius * 2, radius * 2)

        # Create the mask
        mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        pygame.draw.circle(mask, (255, 255, 255, 50), (radius, radius), radius)

        # Apply texture on mask
        mask.blit(self.action_radius_texture, (0, 0), None, pygame.BLEND_MULT)
        mask_rect = mask.get_rect()
        mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)




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

        self.pm_sensor.collision_type = collision_types['activable']


    def actionate(self):

        self.pm_shape.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


@ActionableGenerator.register_subclass('edible')
class EdibleObject(ActionableObject):


    def __init__(self, params):


        super(EdibleObject, self).__init__(params)

        self.shrink_when_eaten = params['shrink_when_eaten']

        self.pm_sensor.collision_type = collision_types['edible']

        self.reward = params.get('initial_reward', 0)


    def actionate(self):

        self.reward = self.reward*self.shrink_when_eaten

        # TODO: refactor the parent class to generate shapes easily

        if self.physical_shape == 'rectangle':
            self.shape_rectangle = [ x* self.shrink_when_eaten for x in self.shape_rectangle ]
        else :
            self.radius = self.radius * self.shrink_when_eaten

        if self.physical_shape in ['triangle', 'pentagon'] :
            self.compute_vertices()

        if self.movable:
            self.mass = self.mass * self.shrink_when_eaten
            inertia = self.compute_moments()
            pm_body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)


        pm_body.position = self.position[:2]
        pm_body.angle = self.position[2]

        self.pm_shape = self.generate_pymunk_shape(pm_body)

        self.pm_shape.friction = 1.
        # self.shape.group = 1
        self.pm_shape.elasticity = 0.95

        self.pm_body = pm_body


        shape_sensor = self.generate_pymunk_sensor_shape(self.pm_body)

        self.pm_sensor = shape_sensor
        self.pm_sensor.collision_type = collision_types['edible']

        self.texture_surface = None
        self.action_radius_texture = None


#        self.__init__(self.params)
        #self.initialize_texture()


@ActionableGenerator.register_subclass('dispenser')
class DispenserObject(ActionableObject):

    def __init__(self, params):

        super(DispenserObject, self).__init__(params)

        self.pm_sensor.collision_type = collision_types['activable']

        self.object_produced = params['object_produced']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.limit = params['limit']

        self.produced_elements = []


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

        self.pm_sensor.collision_type = collision_types['graspable']

        self.graspable = True

    def actionate(self):
        pass



@ActionableGenerator.register_subclass('door_opener')
class DoorObject(ActionableObject):

    def __init__(self, params):

        super(DoorObject, self).__init__(params)

        self.pm_sensor.collision_type = collision_types['activable']

        self.door_params = params['door']

        self.time_open = params['time_open']

        self.door_opened = False

    def assign_door(self, door):

        self.door = door

    def start_timer(self):

        self.timer = self.time_open

    def update_timer(self):

        self.timer -= 1



