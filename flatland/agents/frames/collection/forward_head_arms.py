import pymunk, pygame
from .forward_head import ForwardHead
from flatland.agents.frames.frame import *
from flatland.utils import texture

from pygame.locals import *

from flatland.default_parameters.agents import *


@FrameGenerator.register_subclass('forward_head_arms')
class ForwardHeadArms(ForwardHead):

    def __init__(self, agent_params):

        agent_params = {**forward_head_arms_default, **agent_params}
        super(ForwardHeadArms, self).__init__(agent_params)


        self.arm1_range = agent_params.get('arm_rotation_range')
        self.arm1_speed = agent_params.get('arm_rotation_speed')
        self.arm1_radius = agent_params.get("arm_radius")
        self.arm1_mass = agent_params.get("arm_mass")
        self.arm1_metabolism = agent_params.get("arm_metabolism")

        arm1 = FrameParts()

        base = self.anatomy["base"]

        self.arm1_length = 10
        self.arm1_width = 40

        inertia = pymunk.moment_for_box(self.arm1_mass, (self.arm1_width, self.arm1_length))

        dist_to_body = 50

        body = pymunk.Body(self.arm1_mass, inertia)
        body.position = [self.anatomy['base'].body.position[0]+dist_to_body, \
        self.anatomy['base'].body.position[1]]
        #import pdb;pdb.set_trace()
        body.angle = self.anatomy['base'].body.angle 

        arm1.body = body

        shape = pymunk.Poly.create_box(body, (self.arm1_width, self.arm1_length))
        shape.sensor = False

        arm1.shape = shape

        arm1.joint = [ pymunk.PinJoint(arm1.body, base.body, (0, self.arm1_width/2), (dist_to_body, 0)),
                       pymunk.SimpleMotor(arm1.body, base.body, 0)
                       ]

        self.anatomy["arm1"] = arm1

        text = agent_params.get('arm_texture')
        self.arm1_texture = texture.Texture.create(text)
        self.initialize_arm_texture()

        self.arm_velocity = 0


    """def initialize_arm_texture(self):

        # Head
        radius = int(self.arm1_radius)

        # Create a texture surface with the right dimensions
        self.arm1_texture_surface = self.arm1_texture.generate(radius * 2, radius * 2)

        # Create the mask
        self.mask_arm1 = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.mask_arm1.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm1, (255, 255, 255, 255), (0,10,100,110))

        # Apply texture on mask
        self.mask_arm1.blit(self.arm1_texture_surface, (0, 0), None, pygame.BLEND_MULT)
        pygame.draw.line(self.mask_arm1, pygame.color.THECOLORS["blue"], (radius, radius), (radius, 2 * radius), 2)


        width, length = int(self.width), int(self.length)

        if self.texture_visible_surface is None:
            self.texture_visible_surface = text.generate(length, width)
        else:
            self.texture_visible_surface = pygame.transform.scale(self.texture_visible_surface, ((length, width)))

        self.mask_arm1 = pygame.Surface((length, width), pygame.SRCALPHA)
        self.mask_arm1.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm1, (255, 255, 255, alpha), ((0, 0), (length, width)))"""


    def initialize_arm_texture(self):

        width, length = int(self.arm1_width), int(self.arm1_length)

        #if self.texture_visible_surface is None:
        if True:
            self.texture_visible_surface = self.arm1_texture.generate(length, width)
        else:
            self.texture_visible_surface = pygame.transform.scale(self.texture_visible_surface, ((length, width)))

        self.mask_arm1 = pygame.Surface((length, width), pygame.SRCALPHA)
        self.mask_arm1.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm1, (255, 255, 255, 255), ((0, 0), (length, width)))

    def initialize_head_texture(self):

        # Head
        radius = int(self.head_radius)

        # Create a texture surface with the right dimensions
        self.head_texture_surface = self.head_texture.generate(radius * 2, radius * 2)

        # Create the mask
        self.mask_head = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.mask_head.fill((0, 0, 0, 0))
        pygame.draw.circle(self.mask_head, (255, 255, 255, 255), (radius, radius), radius)

        # Apply texture on mask
        self.mask_head.blit(self.head_texture_surface, (0, 0), None, pygame.BLEND_MULT)
        pygame.draw.line(self.mask_head, pygame.color.THECOLORS["blue"], (radius, radius), (radius, 2 * radius), 2)



    def get_head_angle(self):

        a_head = self.anatomy["head"].body.angle
        a_base = self.anatomy["base"].body.angle

        rel_head = (a_base - a_head) % (2*math.pi)
        rel_head = rel_head - 2*math.pi if rel_head > math.pi else rel_head

        return rel_head

    def apply_actions(self, action_commands):

        super().apply_actions(action_commands)

        self.head_velocity = self.actions.get('head_velocity', 0)

        self.anatomy['head'].body.angle +=  self.head_speed * self.head_velocity

        if self.get_head_angle() < -self.head_range:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle + self.head_range
        elif self.get_head_angle() > self.head_range:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle - self.head_range



    def get_movement_energy(self):

        energy = super().get_movement_energy()
        energy['head'] = abs(self.head_velocity)

        return energy

    def get_default_key_mapping(self):

        mapping = super().get_default_key_mapping()

        mapping[K_z] = ['press_hold', 'head_velocity', 1]
        mapping[K_x] = ['press_hold', 'head_velocity', -1]

        return mapping

    def get_available_actions(self):
        actions = super().get_available_actions()

        actions['head_velocity'] = [-1, 1, 'continuous']

        return actions

    def draw(self, surface):
        super().draw(surface)

        mask = pygame.transform.rotate(self.mask_arm1, self.anatomy['arm1'].body.angle * 180 / math.pi)

        mask_rect = mask.get_rect()
        mask_rect.center = self.anatomy['arm1'].body.position[1], self.anatomy['arm1'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)

