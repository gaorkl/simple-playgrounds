from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import *

from flatland.utils.position_sampler import PositionAreaSampler
import pymunk


class Edible(Entity):

    entity_type = 'edible'
    interactive = True
    edible = True

    def __init__(self, position, default_config_key = None, **kwargs):

        default_config = self.parse_configuration('interactive', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Edible, self).__init__(position=position, **entity_params)

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

        if self.initial_reward > 0 and self.reward > self.min_reward:
            return False
        elif self.initial_reward < 0 and self.reward < self.min_reward:
            return False
        else:
            return True

    def reset(self, new_position = None):

        super().reset()

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


class Apple(Edible):

    def __init__(self, position, **kwargs):

        super(Apple, self).__init__(position=position, default_config_key='apple', **kwargs)

class RottenApple(Edible):

    def __init__(self, position, **kwargs):

        super(RottenApple, self).__init__(position=position, default_config_key='rotten_apple', **kwargs)


class Dispenser(Entity):

    entity_type = 'dispenser'
    interactive = True

    def __init__(self, position, entity_produced, entity_produced_params = None, production_area = None, **kwargs):

        default_config = self.parse_configuration('interactive', 'dispenser')
        entity_params = {**default_config, **kwargs}

        super(Dispenser, self).__init__(position=position, **entity_params)


        self.entity_produced = entity_produced

        if entity_produced_params is None:
            self.entity_produced_params = {}
        else:
            self.entity_produced_params = entity_produced_params

        if production_area is None:
            self.local_dispenser = True
            self.location_sampler = PositionAreaSampler(area_shape='circle',
                                                        center=[0, 0],
                                                        radius=self.radius + 10)
        else:
            self.local_dispenser = False
            self.location_sampler = production_area

        self.prodution_limit = entity_params['production_limit']
        self.produced_entities = []

    def activate(self):

        if self.local_dispenser:
            position = self.location_sampler.sample( [self.position[0], self.position[1] ])
        else:
            position = self.location_sampler.sample( )

        obj = self.entity_produced(position = position, is_temporary_entity = True, **self.entity_produced_params)

        return obj

    def reset(self):

        self.produced_entities = []
        replace = super().reset()

        return replace


class Key(Entity):

    entity_type = 'key'
    movable = True

    def __init__(self, position, **kwargs):

        default_config = self.parse_configuration('interactive', 'key')
        entity_params = {**default_config, **kwargs}

        super(Key, self).__init__(position=position, **entity_params)

        self.pm_visible_shape.collision_type = collision_types['gem']


class Chest(Entity):

    entity_type = 'chest'
    interactive = True

    def __init__(self, position, key, treasure, **kwargs):

        default_config = self.parse_configuration('interactive', 'chest')
        entity_params = {**default_config, **kwargs}

        super(Chest, self).__init__(position = position, **entity_params)

        self.key = key
        self.treasure = treasure
        self.treasure.is_temporary_entity = True

        self.reward = entity_params.get('reward')
        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    def activate(self):

        self.treasure.initial_position = self.position
        return self.treasure

    def reset(self):

        self.reward_provided = False
        super().reset()



class Coin(Entity):

    entity_type = 'coin'
    movable = True

    def __init__(self, position, **kwargs):

        default_config = self.parse_configuration('interactive', 'coin')
        entity_params = {**default_config, **kwargs}

        super(Coin, self).__init__(position=position, **entity_params)

        self.pm_visible_shape.collision_type = collision_types['gem']


class VendingMachine(Entity):

    entity_type = 'vending_machine'
    interactive = True

    def __init__(self, position, **kwargs):

        default_config = self.parse_configuration('interactive', 'vending_machine')
        entity_params = {**default_config, **kwargs}

        super(VendingMachine, self).__init__(position = position, **entity_params)

        self.reward = entity_params.get('reward')


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
        super().reset()


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

