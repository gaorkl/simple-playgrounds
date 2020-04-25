from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.position_sampler import PositionAreaSampler
import pymunk

import os, yaml

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'activable_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)

@EntityGenerator.register_subclass('edible')
class Edible(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'edible'

        params = {**default_config['edible'], **custom_params}


        params['visible'] = True
        params['interactive'] = True

        super(Edible, self).__init__(params)

        self.shrink_ratio_when_eaten = params['shrink_ratio_when_eaten']

        self.reward = params.get('initial_reward', 0)
        self.min_reward = params.get('min_reward', 0)
        self.edible = True

    def generate_shapes_and_masks(self):

        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            self.visible_vertices = self.compute_vertices(self.radius)

        self.generate_pm_visible_shape()
        self.visible_mask = self.generate_visible_mask()

        self.generate_pm_interaction_shape()
        self.interaction_mask = self.generate_interaction_mask()

        self.pm_elements = [self.pm_body, self.pm_visible_shape, self.pm_interaction_shape]

    def activate(self):

        # Change reward, size and mass

        position = self.pm_body.position
        angle = self.pm_body.angle

        self.reward = self.reward*self.shrink_ratio_when_eaten


        if self.movable:
            self.mass = self.mass * self.shrink_ratio_when_eaten
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)
            self.pm_body.position = position
            self.pm_body.angle = angle

        if self.physical_shape == 'rectangle':
            self.width = self.width * self.shrink_ratio_when_eaten
            self.length = self.length * self.shrink_ratio_when_eaten
        else :
            self.radius = self.radius * self.shrink_ratio_when_eaten


        ##### PyMunk sensor shape
        if self.physical_shape == 'rectangle':
            self.width_interaction = self.width + self.interaction_range
            self.length_interaction = self.length + self.interaction_range

        else:
            self.radius_interaction = self.radius + self.interaction_range
            self.interaction_vertices = self.compute_vertices(self.radius_interaction)

        self.generate_shapes_and_masks()

    def reset(self, new_position = None):

        replace = super().reset()

        self.reward = self.params.get('initial_reward', 0)
        self.mass = self.params['mass']

        position = self.pm_body.position
        angle = self.pm_body.angle

        if self.movable:
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)
            self.pm_body.position = position
            self.pm_body.angle = angle


        if self.physical_shape == 'rectangle':
            self.width, self.length = self.params['shape_rectangle']
            self.width = self.width
            self.width_interaction = self.width + self.interaction_range
            self.length_interaction = self.length + self.interaction_range


        else:
            self.radius = self.params['radius']
            self.radius_interaction = self.radius + self.interaction_range
            self.interaction_vertices = self.compute_vertices(self.radius_interaction)


        self.generate_shapes_and_masks()

        return replace


@EntityGenerator.register_subclass('dispenser')
class Dispenser(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'dispenser'

        params = {**default_config['dispenser'], **custom_params}
        params['visible'] = True
        params['interactive'] = True

        super(Dispenser, self).__init__(params)

        self.entity_produced = params['entity_produced']

        self.local_dispenser = False
        self.location_sampler = params.get('area', None)

        if self.location_sampler is None:
            self.local_dispenser = True
            self.location_sampler = PositionAreaSampler(area_shape ='circle', center = [self.position[0], self.position[1]], radius =self.radius + 10)


        self.prodution_limit = params['production_limit']

        self.produced_elements = []

    def activate(self):

        obj = self.entity_produced

        if self.local_dispenser:
            position = self.location_sampler.sample( [self.position[0], self.position[1] ])
        else:
            position = self.location_sampler.sample( )

        obj['position'] = position

        return obj.copy()

    def reset(self):

        self.produced_elements = []
        replace = super().reset()

        return replace
#
# #TODO: class button-door, then sublcasses
#
# @EntityGenerator.register_subclass('button_door_openclose')
# class ButtonDoorOpenClose(Entity):
#
#     def __init__(self, params):
#
#         params = {**button_door_openclose_default, **params}
#         params['visible'] = True
#         params['interactive'] = True
#
#         super(ButtonDoorOpenClose, self).__init__(params)
#
#         self.activable = True
#
#         self.door_params = {**door_default, **params['door']}
#         self.door_opened = False
#
#         self.door = None
#
#
#     def activate(self):
#
#         if self.door_opened:
#             self.door_opened = False
#             self.door.visible = True
#
#         else:
#             self.door_opened = True
#             self.door.visible = False
#
#     def reset(self):
#
#         self.door_opened = False
#         self.door.visible = True
#         replace = super().reset()
#
#         return replace
#
#
# @EntityGenerator.register_subclass('button_door_opentimer')
# class ButtonDoorOpenTimer(Entity):
#
#     def __init__(self, params):
#
#         params = {**button_door_opentimer_default, **params}
#         params['visible'] = True
#         params['interactive'] = True
#
#         super(ButtonDoorOpenTimer, self).__init__(params)
#
#         self.activable = True
#
#         self.door_params = {**door_default, **params['door']}
#         self.time_open = params['time_open']
#
#
#         self.timer = self.time_open
#         self.door = None
#         self.door_opened = False
#
#     def close_door(self):
#
#         self.door_opened = False
#         self.reset_timer()
#
#     def activate(self):
#
#         self.door.visible = False
#         self.reset_timer()
#
#     def reset_timer(self):
#
#         self.timer = self.time_open
#
#     def update(self):
#
#         if self.door_opened:
#             self.timer -= 1
#
#         if self.timer == 0:
#             self.door.visible = True
#
#     def reset(self):
#
#         self.timer = self.time_open
#         self.door_opened = False
#         self.door.visible = True
#         replace = super().reset()
#
#         return replace
#
#
#
# @EntityGenerator.register_subclass('lock_key_door')
# class LockKeyDoor(Entity):
#
#     def __init__(self, params):
#
#         params = {**lock_key_door_default, **params}
#         params['visible'] = True
#         params['interactive'] = True
#
#         super(LockKeyDoor, self).__init__(params)
#
#         self.activable = True
#
#         self.door_params = {**door_default, **params['door']}
#         self.key_params = {**door_default, **params['key']}
#
#         self.door_opened = False
#
#         self.door = None
#         self.key = None
#
#     def activate(self):
#
#         self.door_opened = True
#         self.door.visible = False
#
#     def reset(self):
#
#         self.door_opened = False
#         self.door.visible = True
#         replace = super().reset()
#
#         return replace
#
#
#
# @EntityGenerator.register_subclass('chest')
# class Chest(Entity):
#
#     def __init__(self, params):
#
#         params = {**chest_default, **params}
#         params['visible'] = True
#         params['interactive'] = True
#
#         super(Chest, self).__init__(params)
#
#         self.activable = True
#
#         self.key_params = {**key_chest_default, **params['key_pod']}
#
#         self.reward = params.get('reward', 0)
#         self.reward_provided = False
#
#
#     def pre_step(self):
#
#         self.reward_provided = False
#
#     def get_reward(self):
#
#         if not self.reward_provided:
#             self.reward_provided = True
#             return self.reward
#
#         else:
#             return 0
#
#     def reset(self):
#
#         self.reward_provided = False
#         replace = super().reset()
#
#         return replace
#
# @EntityGenerator.register_subclass('gem')
# class Gem(Entity):
#
#     def __init__(self, params ):
#         """
#         Instantiate an obstacle with the following parameters
#         :param pos: 2d tuple or 'random', position of the fruit
#         :param environment: the environment calling the creation of the fruit
#         """
#
#         params = {**basic_default, **params}
#         params['visible'] = True
#         params['interactive'] = True
#
#         super(Gem, self).__init__(params)
#
#         self.pm_visible_shape.collision_type = collision_types['gem']
