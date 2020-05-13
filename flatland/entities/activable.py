from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import *

from flatland.utils.position_sampler import PositionAreaSampler
import pymunk



@EntityGenerator.register_subclass('edible')
class Edible(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'edible'
        self.interactive =  True
        self.edible = True

        default_config = self.parse_configuration('activable', 'edible')
        entity_params = {**default_config, **custom_params}

        super(Edible, self).__init__(entity_params)

        self.shrink_ratio_when_eaten = entity_params['shrink_ratio_when_eaten']
        self.min_reward = entity_params['min_reward']

        self.initial_reward = entity_params['initial_reward']
        if self.physical_shape == 'rectangle':
            self.initial_width, self.initial_length = entity_params['shape_rectangle']
        else:
            self.initial_radius = entity_params['radius']
        self.initial_mass = self.mass

        self.reward = self.initial_reward

        # self.params = entity_params


    def generate_shapes_and_masks(self):

        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            self.visible_vertices = self.compute_vertices(self.radius)

        self.create_pm_visible_shape()
        self.create_visible_mask()

        self.create_pm_interaction_shape()
        self.create_interaction_mask()

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

        self.reward = self.initial_reward
        self.mass = self.initial_mass

        position = self.pm_body.position
        angle = self.pm_body.angle



        #self.create_pm_body()

        if self.movable:
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)
            self.pm_body.position = position
            self.pm_body.angle = angle


        if self.physical_shape == 'rectangle':
            self.width, self.length = self.initial_width, self.initial_length
            self.width_interaction = self.width + self.interaction_range
            self.length_interaction = self.length + self.interaction_range
        else:
            self.radius = self.initial_radius
            self.radius_interaction = self.radius + self.interaction_range
            self.interaction_vertices = self.compute_vertices(self.radius_interaction)


        self.generate_shapes_and_masks()

        return replace


@EntityGenerator.register_subclass('dispenser')
class Dispenser(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'dispenser'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'dispenser')
        entity_params = {**default_config, **custom_params}


        super(Dispenser, self).__init__(entity_params)

        absorbable_config = self.parse_configuration('basic', 'absorbable')
        self.entity_produced = entity_params.get('entity_produced', absorbable_config)

        self.local_dispenser = False
        self.location_sampler = entity_params.get('area', None)

        if self.location_sampler is None:
            self.local_dispenser = True
            self.location_sampler = PositionAreaSampler(area_shape ='circle', center = [self.position[0], self.position[1]], radius =self.radius + 10)


        self.prodution_limit = entity_params['production_limit']

        self.produced_entities = []

    def activate(self):

        obj = self.entity_produced

        if self.local_dispenser:
            position = self.location_sampler.sample( [self.position[0], self.position[1] ])
        else:
            position = self.location_sampler.sample( )

        obj['position'] = position

        return obj.copy()

    def reset(self):

        self.produced_entities = []
        replace = super().reset()

        return replace


@EntityGenerator.register_subclass('door')
class Door(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'door'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'door')
        entity_params = {**default_config, **custom_params}


        super(Door, self).__init__(entity_params)

        self.opened = False


    def open_door(self):

        self.opened = True
        self.visible = False


    def close_door(self):
        self.opened = False
        self.visible = True


    def reset(self):

        self.close_door()
        replace = super().reset()

        return replace

@EntityGenerator.register_subclass('openclose_switch')
class OpenCloseSwitch(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'switch'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'switch')
        entity_params = {**default_config, **custom_params}

        super(OpenCloseSwitch, self).__init__(entity_params)

        self.door = entity_params['door']

    def activate(self):

         if self.door.opened:
             self.door.close_door()

         else:
             self.door.open_door()


@EntityGenerator.register_subclass('timer_switch')
class TimerSwitch(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'switch'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'switch')
        entity_params = {**default_config, **custom_params}


        super(TimerSwitch, self).__init__(entity_params)

        self.activable = True

        self.door = entity_params['door']

        self.time_open = entity_params['time_open']
        self.timer = self.time_open


    def activate(self):

        self.door.open_door()
        self.reset_timer()

    def reset_timer(self):

        self.timer = self.time_open

    def update(self):

        if self.door.opened:
            self.timer -= 1


    def reset(self):

        self.timer = self.time_open
        self.door.close_door()

        replace = super().reset()

        return replace



@EntityGenerator.register_subclass('lock')
class Lock(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'lock'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'lock')
        entity_params = {**default_config, **custom_params}

        super(Lock, self).__init__(entity_params)

        self.door = entity_params['door']
        self.key = entity_params['key']


    def activate(self):

        self.door.open_door()

@EntityGenerator.register_subclass('key')
class Key(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'key'
        self.movable = True

        default_config = self.parse_configuration('activable', 'key')
        entity_params = {**default_config, **custom_params}

        super(Key, self).__init__(entity_params)

        self.pm_visible_shape.collision_type = collision_types['gem']

@EntityGenerator.register_subclass('chest')
class Chest(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'chest'
        self.interactive = True

        default_config = self.parse_configuration('activable', 'chest')
        entity_params = {**default_config, **custom_params}


        super(Chest, self).__init__(entity_params)

        self.key = entity_params['key']

        self.reward = entity_params.get('reward')
        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self.reward

        else:
            return 0

    def reset(self):

        self.reward_provided = False
        replace = super().reset()

        return replace
