from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import *

from flatland.utils.position_sampler import PositionAreaSampler
import pymunk



@EntityGenerator.register_subclass('edible')
class Edible(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'edible'

        default_config = self.parse_configuration('activable', 'edible')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

        super(Edible, self).__init__(entity_params)

        self.shrink_ratio_when_eaten = entity_params['shrink_ratio_when_eaten']

        self.reward = entity_params['initial_reward']
        self.min_reward = entity_params['min_reward']

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

        default_config = self.parse_configuration('activable', 'dispenser')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

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

        default_config = self.parse_configuration('activable', 'door')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = False

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

        default_config = self.parse_configuration('activable', 'switch')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

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

        default_config = self.parse_configuration('activable', 'switch')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

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

        default_config = self.parse_configuration('activable', 'lock')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

        super(Lock, self).__init__(entity_params)

        self.door = entity_params['door']
        self.key = entity_params['key']


    def activate(self):

        self.door.open_door()

@EntityGenerator.register_subclass('key')
class Key(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'key'

        default_config = self.parse_configuration('activable', 'key')
        entity_params = {**default_config, **custom_params}

        entity_params['movable'] = True

        super(Key, self).__init__(entity_params)

        self.pm_visible_shape.collision_type = collision_types['gem']

@EntityGenerator.register_subclass('chest')
class Chest(Entity):

    def __init__(self, custom_params):

        self.entity_type = 'chest'

        default_config = self.parse_configuration('activable', 'chest')
        entity_params = {**default_config, **custom_params}

        entity_params['visible'] = True
        entity_params['interactive'] = True

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
