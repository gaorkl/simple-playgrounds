import pymunk, pygame
import math
from .forward import ForwardAgent

# move physical body to utils
from .agent import PhysicalBody

from ..utils.config import *

from pygame.locals import *


class ForwardHeadAgent(ForwardAgent):

    def __init__(self, agent_params):

        super(ForwardHeadAgent, self).__init__(agent_params)

        self.head_range = agent_params.get('head_range', 0)
        self.head_speed = agent_params.get('head_speed', 10)

        head = PhysicalBody()

        base = self.anatomy["base"]

        inertia = pymunk.moment_for_circle(1, 0, self.radius, (0, 0))

        body = pymunk.Body(1, inertia)
        body.position = agent_params['position'][:2]
        body.angle = agent_params['position'][2]

        head.body = body

        shape = pymunk.Circle(body, self.radius-5, (0, 0))
        shape.sensor = True

        head.shape = shape


        head.joint = [ pymunk.PinJoint(head.body, base.body, (0, 0), (0, 0)),
                       pymunk.SimpleMotor(head.body, base.body, 0)
                       ]


        self.anatomy["head"] = head

    def get_head_angle(self):

        a_head = self.anatomy["head"].body.angle
        a_base = self.anatomy["base"].body.angle

        rel_head = (a_base - a_head) % (2*math.pi)
        rel_head = rel_head - 2*math.pi if rel_head > math.pi else rel_head

        return rel_head

    def apply_action(self, actions):
        super().apply_action(actions)

        head_velocity = actions.get('head_velocity', 0)

        self.anatomy['head'].body.angle +=  self.head_speed * head_velocity

        if self.get_head_angle() < -self.head_range:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle + self.head_range
        elif self.get_head_angle() > self.head_range:
            self.anatomy['head'].body.angle = self.anatomy['base'].body.angle - self.head_range




        #self.anatomy["head"].joint

    def getStandardKeyMapping(self):

        mapping = super().getStandardKeyMapping()

        mapping[K_z] = ['press_hold', 'head_velocity', 1]
        mapping[K_x] = ['press_hold', 'head_velocity', -1]

        return mapping

    def getAvailableActions(self):
        actions = super().getAvailableActions()

        actions['head_velocity'] = [-1, 1, 'continuous']

        return actions

    def draw(self, surface):
        super().draw(surface)