import pymunk, math, pygame
from flatland.utils.config import *

from flatland.utils import texture

from flatland.entities.entity import Entity

class ZoneGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, zone_type):
        def decorator(subclass):
            cls.subclasses[zone_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        zone_type = params['zone_type']
        if zone_type not in cls.subclasses:
            #TODO: verify rais eerroe?
            raise ValueError('Zone type not implemented:' + zone_type)

        return cls.subclasses[zone_type](params)

class Zone(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """
        super(Zone, self).__init__()

        # Create shape, the body is static

        self.physical_shape = params['physical_shape']
        self.position = params['position']

        self.reward = params.get('reward', 0)
        self.reward_provided = False

        self.activable = False
        self.movable = False
        self.graspable = False

        if self.physical_shape == 'rectangle':
            self.shape_rectangle = params['shape_rectangle']

        else :
            self.radius = params['radius']

        if self.physical_shape in ['triangle', 'pentagon'] :
            self.compute_vertices()

        pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        pm_body.position = params['position'][0:2]
        pm_body.angle = params['position'][2]

        self.pm_body = pm_body

        shape_sensor = self.generate_pymunk_sensor_shape(self.pm_body)

        self.pm_sensor = shape_sensor

        text = params['texture']
        self.texture = texture.Texture.create(text)
        self.action_radius_texture = None

        self.pm_sensor.collision_type = collision_types['zone']
        self.zone_type = params['zone_type']

    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self.reward

        else:
            return 0

    def compute_vertices(self):

        if self.physical_shape == 'triangle':

            self.vertices = [[0,0], [ 0, self.radius * math.sqrt(3)],
                             [self.radius * 3 / 2.0 , self.radius * math.sqrt(3) / 2.0 ] ]

            self.vertices = [ [v[0] - self.radius / 2.0, v[1] - self.radius* math.sqrt(3) / 2.0] for v in self.vertices]

        elif self.physical_shape == 'pentagon':

            self.vertices = []
            for n in range(5):
                self.vertices.append( [ self.radius*math.cos(n * 2*math.pi / 5), self.radius* math.sin(n * 2*math.pi / 5) ])



    def generate_pymunk_sensor_shape(self, body):


        if self.physical_shape == 'circle':

            shape_sensor = pymunk.Circle(body, self.radius)

        elif self.physical_shape in ['triangle', 'pentagon']:

            shape_sensor = pymunk.Poly(body, self.vertices)

        elif self.physical_shape == 'rectangle':

            shape_sensor = pymunk.Poly.create_box(body, self.shape_rectangle)

        else:

            raise ValueError('Not implemented')

        shape_sensor.sensor = True

        return shape_sensor



    def draw(self, surface):
        """
        Draw the obstacle on the environment screen
        """

        if self.physical_shape == 'circle':
            radius = int(self.radius)

            # Create a texture surface with the right dimensions
            if self.action_radius_texture is None:
                self.action_radius_texture = self.texture.generate(radius * 2, radius * 2)

            # Create the mask
            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, 20), (radius, radius), radius)

            # Apply texture on mask
            mask.blit(self.action_radius_texture, (0, 0), None, pygame.BLEND_MULT)
            mask_rect = mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask, mask_rect, None)

        elif self.physical_shape == 'rectangle':
            width , length = self.shape_rectangle

            # Create a texture surface with the right dimensions
            if self.action_radius_texture is None:
                self.action_radius_texture = self.texture.generate(length, width)

            # Create the mask
            mask = pygame.Surface((length, width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, 20), ((0,0), (length, width)))

            # Apply texture on mask
            mask.blit(self.action_radius_texture, (0, 0), None, pygame.BLEND_MULT)
            mask_rect = mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask, mask_rect, None)


        elif self.physical_shape in ['triangle', 'pentagon']:

            bb = self.pm_shape.cache_bb()
            length = bb.top - bb.bottom
            width = bb.right - bb.left

            vertices = [ [x[1] + length, x[0] + width ] for x in self.vertices ]

            # Create a texture surface with the right dimensions
            if self.action_radius_texture is None:
                self.action_radius_texture = self.texture.generate(2 * length, 2 * width)
                self.mask = pygame.Surface((2*length, 2*width), pygame.SRCALPHA)
                self.mask.fill((0, 0, 0, 0))
                pygame.draw.polygon(self.mask, (255, 255, 255, 20), vertices)

                # Apply texture on mask
                self.mask.blit(self.action_radius_texture, (0, 0), None, pygame.BLEND_MULT)

            mask_rotated = pygame.transform.rotate(self.mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask_rotated, mask_rect, None)




        else:
            raise ValueError('Not implemented')

@ZoneGenerator.register_subclass('end_zone')
class EndZone(Zone):

    def __init__(self, params):

        super(EndZone, self).__init__(params)

        self.reward = params['reward']



