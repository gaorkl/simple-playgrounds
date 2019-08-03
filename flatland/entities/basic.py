import pymunk, math, pygame

from flatland.utils.config import *
from flatland.utils.pygame_utils import to_pygame

from ..common import texture


from flatland.entities.entity import Entity


class BasicObject(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """
        super(BasicObject, self).__init__()

        # Create shape, the body is static

        self.physical_shape = params['physical_shape']
        self.movable = params['movable']
        self.position = params['position']

        self.reward = params.get('reward', 0)

        if self.physical_shape == 'circle':
            self.radius = params['radius']

        elif self.physical_shape == 'box':
            self.size_box = params['size_box']

        elif self.physical_shape == 'poly':
            self.vertices = params['vertices']



        if self.movable:
            self.mass = params['mass']
            inertia = self.compute_moments()
            body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            body = pymunk.Body(body_type=pymunk.Body.STATIC)


        body.position = params['position'][0:2]
        body.angle = params['position'][2]

        self.shape_body = self.generate_pymunk_shape(body)

        self.shape_body.friction = 1.
        # self.shape.group = 1
        self.shape_body.elasticity = 0.95

        self.absorbable = params.get('absorbable', False)
        if self.absorbable == True:
            self.name_id = 'absorbable_' + str(Entity.id_number)
            self.shape_body.collision_type = collision_types['absorbable']

        if 'default_color' in params:
            self.shape_body.color = params['default_color']


        self.body_body = body

        self.default_texture = {
            'type': 'color',
            'color': (100, 100, 100)
        }


        self.text = params.get('texture', None)





    def initialize_texture(self ):

        tex = self.text if self.text != None else self.default_texture

        self.texture_surface = None
        self.texture = texture.Texture.create( tex )



    def generate_pymunk_shape(self, body):


        if self.physical_shape == 'circle':

            shape = pymunk.Circle(body, self.radius)

        elif self.physical_shape == 'poly':

            shape = pymunk.Poly(body, self.vertices)

        elif self.physical_shape == 'box':

            shape = pymunk.Poly.create_box(body, self.size_box)

        else:

            raise ValueError('Not implemented')

        return shape



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



    def draw(self, surface):
        """
        Draw the obstacle on the environment screen
        """

        if self.physical_shape == 'circle':
            radius = int(self.radius)

            # Create a texture surface with the right dimensions
            if self.texture_surface is None:
                self.texture_surface = self.texture.generate(radius * 2, radius * 2)

            # Create the mask
            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)

            # Apply texture on mask
            mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)
            mask_rect = mask.get_rect()
            mask_rect.center = self.body_body.position[1], self.body_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask, mask_rect, None)

        elif self.physical_shape == 'box':
            width , length = self.size_box

            # Create a texture surface with the right dimensions
            if self.texture_surface is None:
                self.texture_surface = self.texture.generate(length, width)
                self.texture_surface.set_colorkey((0, 0, 0, 0))

            # Rotate and center the texture
            texture_surface = pygame.transform.rotate(self.texture_surface, self.body_body.angle * 180 / math.pi)
            texture_surface_rect = texture_surface.get_rect()
            #texture_surface_rect.center = to_pygame(self.body_body.position, surface)
            texture_surface_rect.center = self.body_body.position[1], self.body_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(texture_surface, texture_surface_rect, None)

        # elif self.shape == 'composite':
        #     for obstacle in self.obstacles:
        #         obstacle.draw()