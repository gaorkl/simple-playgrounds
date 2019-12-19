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

        base = self.anatomy['base']

        self.eyelid = 1

        ### Arm 1

        ## First part

        self.arm1_range = agent_params.get('arm_rotation_range')
        self.arm1_speed = agent_params.get('arm_rotation_speed')
        self.arm1_radius = agent_params.get("arm_radius")
        self.arm1_mass = agent_params.get("arm_mass")
        self.arm1_metabolism = agent_params.get("arm_metabolism")

        arm1 = FrameParts()

        self.arm1_length = 50
        self.arm1_width = 5

        inertia = pymunk.moment_for_box(self.arm1_mass, (self.arm1_width, self.arm1_length))

        dist_to_body = self.base_radius+self.arm1_length/2.0 + 5

        body = pymunk.Body(self.arm1_mass, inertia)
        body.position = [0,  dist_to_body]
        #self.anatomy['base'].body.position[1] ]
        #import pdb;pdb.set_trace()
        #body.angle = self.anatomy['base'].body.angle

        arm1.body = body

        shape = pymunk.Poly.create_box(body, (self.arm1_width, self.arm1_length))
        shape.sensor = False

        arm1.shape = shape

        arm1.joint = [ #pymunk.PinJoint(arm1.body, base.body,  ( 0, -self.arm1_length / 2), (5, 0)),
                       #pymunk.PinJoint(arm1.body, base.body, ( 0, -self.arm1_length / 2), (-5, 0)),
                       pymunk.PivotJoint(arm1.body, base.body, ( 0, dist_to_body-self.arm1_length / 2 - 5 )),
                       pymunk.SimpleMotor(arm1.body, base.body, 0),
                       pymunk.RotaryLimitJoint(arm1.body, base.body, -self.arm1_range, self.arm1_range)
                       ]

        self.anatomy["arm1"] = arm1

        text = agent_params.get('arm_texture')
        self.arm1_texture = texture.Texture.create(text)
        self.initialize_arm_texture()

        self.arm1_velocity = 0

        ## Second part

        arm1_2 = FrameParts()

        dist_to_arm1 = self.arm1_length/2.0 + 85

        body = pymunk.Body(self.arm1_mass, inertia)
        body.position = [0,  dist_to_arm1]
        #self.anatomy['base'].body.position[1] ]
        #import pdb;pdb.set_trace()
        #body.angle = self.anatomy['base'].body.angle

        arm1_2.body = body

        shape = pymunk.Poly.create_box(body, (self.arm1_width, self.arm1_length))
        shape.sensor = False

        arm1_2.shape = shape

        arm1_2.joint = [#pymunk.PinJoint(arm1_2.body, arm1.body,  (0, -self.arm1_length / 2), (30, 0)),
                       pymunk.PivotJoint(arm1_2.body, arm1.body, ( 0, dist_to_arm1-self.arm1_length / 2)),
                       pymunk.SimpleMotor(arm1_2.body, arm1.body, 0),
                       pymunk.RotaryLimitJoint(arm1_2.body, arm1.body, -self.arm1_range, self.arm1_range)
                       ]

        self.anatomy["arm1_2"] = arm1_2

        text = agent_params.get('arm_texture')
        self.arm1_2_texture = texture.Texture.create(text)
        self.initialize_arm_texture()

        self.arm1_2_velocity = 0

        self.arm1_2_speed = agent_params.get('arm_rotation_speed')

        ### Arm 2

        ## First part

        self.arm2_range = agent_params.get('arm_rotation_range')
        self.arm2_speed = agent_params.get('arm_rotation_speed')
        self.arm2_radius = agent_params.get("arm_radius")
        self.arm2_mass = agent_params.get("arm_mass")
        self.arm2_metabolism = agent_params.get("arm_metabolism")

        arm2 = FrameParts()

        self.arm2_length = 50
        self.arm2_width = 5

        inertia = pymunk.moment_for_box(self.arm2_mass, (self.arm2_width, self.arm2_length))

        dist_to_body = self.base_radius+self.arm2_length/2.0 + 5

        body = pymunk.Body(self.arm2_mass, inertia)
        body.position = [0,  -dist_to_body]
        #self.anatomy['base'].body.position[1] ]
        #import pdb;pdb.set_trace()
        #body.angle = self.anatomy['base'].body.angle

        arm2.body = body

        shape = pymunk.Poly.create_box(body, (self.arm2_width, self.arm2_length))
        shape.sensor = False

        arm2.shape = shape

        arm2.joint = [ #pymunk.PinJoint(arm1.body, base.body,  ( 0, -self.arm1_length / 2), (5, 0)),
                       #pymunk.PinJoint(arm1.body, base.body, ( 0, -self.arm1_length / 2), (-5, 0)),
                       pymunk.PivotJoint(arm2.body, base.body, ( 0, -dist_to_body+self.arm1_length / 2 + 5 )),
                       pymunk.SimpleMotor(arm2.body, base.body, 0),
                       pymunk.RotaryLimitJoint(arm2.body, base.body, -self.arm1_range, self.arm1_range)
                       ]

        self.anatomy["arm2"] = arm2

        text = agent_params.get('arm_texture')
        self.arm2_texture = texture.Texture.create(text)
        self.initialize_arm_texture()

        self.arm2_velocity = 0

        ## Second part

        arm2_2 = FrameParts()

        dist_to_arm2 = self.arm2_length/2.0 + 85

        body = pymunk.Body(self.arm2_mass, inertia)
        body.position = [0,  -dist_to_arm2]
        #self.anatomy['base'].body.position[1] ]
        #import pdb;pdb.set_trace()
        #body.angle = self.anatomy['base'].body.angle

        arm2_2.body = body

        shape = pymunk.Poly.create_box(body, (self.arm2_width, self.arm2_length))
        shape.sensor = False

        arm2_2.shape = shape

        arm2_2.joint = [#pymunk.PinJoint(arm1_2.body, arm1.body,  (0, -self.arm1_length / 2), (30, 0)),
                       pymunk.PivotJoint(arm2_2.body, arm2.body, ( 0, -dist_to_arm2+self.arm2_length / 2)),
                       pymunk.SimpleMotor(arm2_2.body, arm2.body, 0),
                       pymunk.RotaryLimitJoint(arm1_2.body, arm1.body, -self.arm2_range, self.arm2_range)
                       ]

        arm2_2.visible = True

        self.anatomy["arm2_2"] = arm2_2

        text = agent_params.get('arm_texture')
        self.arm2_2_texture = texture.Texture.create(text)
        self.initialize_arm_texture()

        self.arm2_2_velocity = 0

        self.arm2_2_speed = agent_params.get('arm_rotation_speed')


        

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

        # Apply texture on mask
        self.mask_arm1.blit(self.texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)

        self.mask_arm1_2 = pygame.Surface((length, width), pygame.SRCALPHA)
        self.mask_arm1_2.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm1_2, (255, 255, 255, 255), ((0, 0), (length, width)))

        # Apply texture on mask
        self.mask_arm1_2.blit(self.texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)

        self.mask_arm2 = pygame.Surface((length, width), pygame.SRCALPHA)
        self.mask_arm2.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm2, (255, 255, 255, 255), ((0, 0), (length, width)))

        # Apply texture on mask
        self.mask_arm2.blit(self.texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)

        self.mask_arm2_2 = pygame.Surface((length, width), pygame.SRCALPHA)
        self.mask_arm2_2.fill((0, 0, 0, 0))
        pygame.draw.rect(self.mask_arm2_2, (255, 255, 255, 255), ((0, 0), (length, width)))

        # Apply texture on mask
        self.mask_arm2_2.blit(self.texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)



    def get_arm1_angle(self):

        a_arm1 = self.anatomy["arm1"].body.angle
        a_base = self.anatomy["base"].body.angle

        rel_arm1 = (a_base - a_arm1) % (2*math.pi)
        rel_arm1 = rel_arm1 - 2*math.pi if rel_arm1 > math.pi else rel_arm1

        return rel_arm1

    def get_arm1_2_angle(self):

        a_arm1_2 = self.anatomy["arm1_2"].body.angle
        a_arm1 = self.anatomy["arm1"].body.angle

        rel_arm1_2 = (a_arm1 - a_arm1_2) % (2*math.pi)
        rel_arm1_2 = rel_arm1_2 - 2*math.pi if rel_arm1_2 > math.pi else rel_arm1_2

        return rel_arm1_2

    def get_arm2_angle(self):

        a_arm2 = self.anatomy["arm2"].body.angle
        a_base = self.anatomy["base"].body.angle

        rel_arm2 = (a_base - a_arm2) % (2*math.pi)
        rel_arm2 = rel_arm2 - 2*math.pi if rel_arm2 > math.pi else rel_arm2

        return rel_arm2

    def get_arm2_2_angle(self):

        a_arm2_2 = self.anatomy["arm2_2"].body.angle
        a_arm2 = self.anatomy["arm2"].body.angle

        rel_arm2_2 = (a_arm2 - a_arm2_2) % (2*math.pi)
        rel_arm2_2 = rel_arm2_2 - 2*math.pi if rel_arm2_2 > math.pi else rel_arm2_2

        return rel_arm2_2

    def apply_actions(self, action_commands):

        super().apply_actions(action_commands)

        self.arm1_velocity = self.actions.get('arm1_velocity', 0)
        to_add_arm1 = self.arm1_speed * self.arm1_velocity
        self.anatomy['arm1'].body.angle += to_add_arm1

        self.arm1_2_velocity = self.actions.get('arm1_2_velocity', 0)
        to_add_arm1_2 = self.arm1_2_speed * self.arm1_2_velocity
        self.anatomy['arm1_2'].body.angle += to_add_arm1_2

        if self.get_arm1_angle() <= -self.arm1_range:
            self.anatomy['arm1'].body.angle = self.anatomy['base'].body.angle + self.arm1_range

        if self.get_arm1_angle() >= self.arm1_range:
            self.anatomy['arm1'].body.angle = self.anatomy['base'].body.angle - self.arm1_range

        if self.get_arm1_2_angle() <= -self.arm1_range:
            self.anatomy['arm1_2'].body.angle = self.anatomy['arm1'].body.angle + self.arm1_range

        if self.get_arm1_2_angle() >= self.arm1_range:
            self.anatomy['arm1_2'].body.angle = self.anatomy['arm1'].body.angle - self.arm1_range

        self.arm2_velocity = self.actions.get('arm2_velocity', 0)
        to_add_arm2 = self.arm2_speed * self.arm2_velocity
        self.anatomy['arm2'].body.angle += to_add_arm2

        self.arm2_2_velocity = self.actions.get('arm2_2_velocity', 0)
        to_add_arm2_2 = self.arm2_2_speed * self.arm2_2_velocity
        self.anatomy['arm2_2'].body.angle += to_add_arm2_2

        if self.get_arm2_angle() <= -self.arm2_range:
            self.anatomy['arm2'].body.angle = self.anatomy['base'].body.angle + self.arm2_range

        if self.get_arm2_angle() >= self.arm2_range:
            self.anatomy['arm2'].body.angle = self.anatomy['base'].body.angle - self.arm2_range

        if self.get_arm2_2_angle() <= -self.arm2_range:
            self.anatomy['arm2_2'].body.angle = self.anatomy['arm2'].body.angle + self.arm2_range

        if self.get_arm2_2_angle() >= self.arm1_range:
            self.anatomy['arm2_2'].body.angle = self.anatomy['arm2'].body.angle - self.arm2_range

        self.eyelid += self.actions.get('eyelid', 0)/20

        #print(self.eyelid,self.actions.get('eyelid', 0))

        if self.eyelid > 2:
            self.eyelid = 2
        elif self.eyelid < 0:
            self.eyelid = 0


    def get_default_key_mapping(self):

        mapping = super().get_default_key_mapping()

        mapping[K_e] = ['press_hold', 'arm1_velocity', 1]
        mapping[K_c] = ['press_hold', 'arm1_velocity', -1]

        mapping[K_r] = ['press_hold', 'arm1_2_velocity', 1]
        mapping[K_v] = ['press_hold', 'arm1_2_velocity', -1]

        mapping[K_t] = ['press_hold', 'arm2_velocity', 1]
        mapping[K_b] = ['press_hold', 'arm2_velocity', -1]

        mapping[K_y] = ['press_hold', 'arm2_2_velocity', 1]
        mapping[K_n] = ['press_hold', 'arm2_2_velocity', -1]

        mapping[K_a] = ['press_hold', 'eyelid', 1]
        mapping[K_w] = ['press_hold', 'eyelid', -1]

        return mapping

    def get_available_actions(self):
        actions = super().get_available_actions()

        actions['arm1_velocity'] = [-1, 1, 'continuous']

        actions['arm1_2_velocity'] = [-1, 1, 'continuous']

        actions['arm2_velocity'] = [-1, 1, 'continuous']

        actions['arm2_2_velocity'] = [-1, 1, 'continuous']

        actions['eyelid'] = [-1, 1, 'continuous']

        return actions


    def draw(self, surface, visible_to_self=False):
        super().draw(surface, visible_to_self=visible_to_self)

        #print(self.anatomy['head'].body.angle, 'angle')
        #print(self.eyelid, 'eyelid')

        mask = pygame.transform.rotate(self.mask_arm1, self.anatomy['arm1'].body.angle * 180 / math.pi)

        mask_rect = mask.get_rect()
        mask_rect.center = self.anatomy['arm1'].body.position[1], self.anatomy['arm1'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)

        mask = pygame.transform.rotate(self.mask_arm1_2, self.anatomy['arm1_2'].body.angle * 180 / math.pi)

        mask_rect = mask.get_rect()
        mask_rect.center = self.anatomy['arm1_2'].body.position[1], self.anatomy['arm1_2'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)

        mask = pygame.transform.rotate(self.mask_arm2, self.anatomy['arm2'].body.angle * 180 / math.pi)

        mask_rect = mask.get_rect()
        mask_rect.center = self.anatomy['arm2'].body.position[1], self.anatomy['arm2'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)

        mask = pygame.transform.rotate(self.mask_arm2_2, self.anatomy['arm2_2'].body.angle * 180 / math.pi)

        mask_rect = mask.get_rect()
        mask_rect.center = self.anatomy['arm2_2'].body.position[1], self.anatomy['arm2_2'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask, mask_rect, None)






