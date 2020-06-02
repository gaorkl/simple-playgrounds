from .forward import Forward
from flatland.agents.body_parts.parts import *
from flatland.utils import texture

from pygame.locals import *

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, '../frame_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


@FrameGenerator.register_subclass('forward_head')
class ForwardHead(Forward):

    def __init__(self, agent_params):

        self.agent_type = 'forward_head'
        super(ForwardHead, self).__init__(agent_params)

        # Head
        if agent_params is not None:
            head_params = agent_params.get('head', {})
        else:
            head_params = {}

        self.head_params = {**default_config['head'], **head_params}

        self.head_range = self.head_params.get('rotation_range') * math.pi/180
        self.head_speed = self.head_params.get('rotation_speed')
        self.head_radius = self.head_params.get('radius')
        self.head_mass = self.head_params.get("mass")

        self.head_metabolism = head_params.get("metabolism")

        head = FrameParts()

        base = self.anatomy["base"]

        inertia = pymunk.moment_for_circle( self.head_mass, 0, self.head_radius, (0, 0) )

        body = pymunk.Body(self.head_mass, inertia)
        #body_parts.position = [self.anatomy['base'].body_parts.position[0]+self.base_radius, self.anatomy['base'].body_parts.position[1]]
        #import pdb;pdb.set_trace()
        #body_parts.angle = self.anatomy['base'].body_parts.angle

        head.body = body

        shape = pymunk.Circle(body, self.head_radius, (0, 0))
        shape.sensor = True

        head.shape = shape

        head.joint = [pymunk.PinJoint(head.body, base.body, (0, 0), (0,0)),
                       pymunk.SimpleMotor(head.body, base.body, 0)
                       ]

        self.anatomy["head"] = head

        text = self.head_params.get('texture')
        self.head_texture = texture.Texture.create(text)
        self.initialize_head_texture()

        self.head_velocity = 0



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

        if self.get_head_angle() < -self.head_range/2:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle + self.head_range/2
        elif self.get_head_angle() > self.head_range/2:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle - self.head_range/2



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

    def draw(self, surface, visible_to_self=False):
        super().draw(surface, visible_to_self=visible_to_self)

        if not visible_to_self:
            mask = pygame.transform.rotate(self.mask_head, self.anatomy['head'].body.angle * 180 / math.pi)

            mask_rect = mask.get_rect()
            mask_rect.center = self.anatomy['head'].body.position[1], self.anatomy['head'].body.position[0]

            # Blit the masked texture on the screen
            surface.blit(mask, mask_rect, None)

