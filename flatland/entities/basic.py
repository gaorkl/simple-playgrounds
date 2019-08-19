import pymunk, math, pygame
from flatland.utils.config import *

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
        self.activable = False
        self.position = params['position']

        self.reward = params.get('reward', 0)

        # TODO: replace basic shapes by circle, triangle, rectangle, pentagon , hexagon

        if self.physical_shape == 'rectangle':
            self.shape_rectangle = params['shape_rectangle']

        else :
            self.radius = params['radius']

        if self.physical_shape in ['triangle', 'pentagon'] :
            self.compute_vertices()


        if self.movable:
            self.mass = params['mass']
            inertia = self.compute_moments()
            pm_body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)


        pm_body.position = params['position'][0:2]
        pm_body.angle = params['position'][2]

        self.pm_shape = self.generate_pymunk_shape(pm_body)

        self.pm_shape.friction = 1.
        # self.shape.group = 1
        self.pm_shape.elasticity = 0.95

        self.absorbable = params.get('absorbable', False)
        if self.absorbable == True:
            self.name_id = 'absorbable_' + str(Entity.id_number)
            self.pm_shape.collision_type = collision_types['absorbable']

        if 'default_color' in params:
            self.pm_shape.color = params['default_color']

        self.pm_body = pm_body

        text = params['texture']
        self.texture = texture.Texture.create(text)
        self.texture_surface = None

    def compute_vertices(self):

        if self.physical_shape == 'triangle':

            self.vertices = [[0,0], [ 0, self.radius * math.sqrt(3)],
                             [self.radius * 3 / 2.0 , self.radius * math.sqrt(3) / 2.0 ] ]

            self.vertices = [ [v[0] - self.radius / 2.0, v[1] - self.radius* math.sqrt(3) / 2.0] for v in self.vertices]

        elif self.physical_shape == 'pentagon':

            self.vertices = []
            for n in range(5):
                self.vertices.append( [ self.radius*math.cos(n * 2*math.pi / 5), self.radius* math.sin(n * 2*math.pi / 5) ])




    def generate_pymunk_shape(self, body):


        if self.physical_shape == 'circle':

            shape = pymunk.Circle(body, self.radius)

        elif self.physical_shape in ['triangle', 'pentagon']:

            shape = pymunk.Poly(body, self.vertices)

        elif self.physical_shape == 'rectangle':

            shape = pymunk.Poly.create_box(body, self.shape_rectangle)

        else:

            raise ValueError('Not implemented')

        return shape



    def compute_moments(self):

        if self.physical_shape == 'circle':

            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'pentagon']:

            moment = pymunk.moment_for_poly(self.mass, self.vertices)

        elif self.physical_shape == 'rectangle':

            moment =  pymunk.moment_for_box(self.mass, self.shape_rectangle)

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
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask, mask_rect, None)

        elif self.physical_shape == 'rectangle':
            width , length = self.shape_rectangle

            # Create a texture surface with the right dimensions
            if self.texture_surface is None:
                self.texture_surface = self.texture.generate(length, width)
                self.texture_surface.set_colorkey((0, 0, 0, 0))



            # Rotate and center the texture
            texture_surface = pygame.transform.rotate(self.texture_surface, self.pm_body.angle * 180 / math.pi)
            texture_surface_rect = texture_surface.get_rect()
            #texture_surface_rect.center = to_pygame(self.body_body.position, surface)
            texture_surface_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(texture_surface, texture_surface_rect, None)

        elif self.physical_shape in ['triangle', 'pentagon']:

            bb = self.pm_shape.cache_bb()
            length = bb.top - bb.bottom
            width = bb.right - bb.left

            vertices = [ [x[1] + length, x[0] + width ] for x in self.vertices ]

            # Create a texture surface with the right dimensions
            if self.texture_surface is None:
                self.texture_surface = self.texture.generate(2*length, 2*width )
                self.mask = pygame.Surface((2*length, 2*width), pygame.SRCALPHA)
                self.mask.fill((0, 0, 0, 0))
                pygame.draw.polygon(self.mask, (255, 255, 255, 255), vertices)

                # Apply texture on mask
                self.mask.blit(self.texture_surface, (0, 0), None, pygame.BLEND_MULT)

            mask_rotated = pygame.transform.rotate(self.mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask_rotated, mask_rect, None)




        else:
            print('gnagnagne')
        # elif self.shape == 'composite':
        #     for obstacle in self.obstacles:
        #         obstacle.draw()