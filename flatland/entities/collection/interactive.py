from flatland.entities.entity import *
from flatland.utils.config import *

from flatland.utils.position_utils import PositionAreaSampler
import pymunk


# @EntityGenerator.register('edible')
class Edible(Entity):

    entity_type = 'edible'
    interactive = True
    edible = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for edible entities

        Edible entity provides a reward to the agent that eats it, then shrinks in size, mass, and available reward.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: can be 'apple' or 'rotten_apple'
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            shrink_ratio_when_eaten: When eaten by an agent, the mass, size, and reward are multiplied by this ratio.
                Default: 0.9
            initial_reward: Initial reward of the edible
            min_reward: When reward is lower than min_reward, the edible entity disappears

        """

        default_config = self.parse_configuration('interactive', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Edible, self).__init__(initial_position=initial_position, **entity_params)

        self.shrink_ratio_when_eaten = entity_params['shrink_ratio_when_eaten']
        self.min_reward = entity_params['min_reward']
        self.initial_reward = entity_params['initial_reward']

        self.initial_width, self.initial_length = self.width, self.length
        self.initial_radius = self.radius
        self.initial_mass = self.mass

        self.reward = self.initial_reward

    def generate_shapes_and_masks(self):

        self.pm_visible_shape = self.create_pm_visible_shape()
        self.visible_mask = self.create_visible_mask()

        self.pm_interaction_shape = self.create_pm_interaction_shape()
        self.interaction_mask = self.create_interaction_mask()

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

        self.width = self.width * self.shrink_ratio_when_eaten
        self.length = self.length * self.shrink_ratio_when_eaten
        self.radius = self.radius * self.shrink_ratio_when_eaten
        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range

        # self.interaction_vertices = self.compute_vertices(self.interaction_radius)
        # self.visible_vertices = self.compute_vertices(self.radius)

        self.generate_shapes_and_masks()

        if self.initial_reward > 0 and self.reward > self.min_reward:
            return False
        elif self.initial_reward < 0 and self.reward < self.min_reward:
            return False
        else:
            return True

    def reset(self, new_position=None):

        super().reset()

        self.reward = self.initial_reward
        self.mass = self.initial_mass

        if self.movable:
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)

        self.width, self.length = self.initial_width, self.initial_length
        self.radius = self.initial_radius
        self.visible_vertices = self.compute_body_vertices(self.radius)

        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range
        self.interaction_vertices = self.compute_body_vertices(self.interaction_radius)

        self.generate_shapes_and_masks()



# @EntityGenerator.register('apple')
class Apple(Edible):

    def __init__(self, initial_position, **kwargs):
        """ Edible entity that provides a positive reward

        Default: Green Circle of radius 10, with an initial_reward of 30, a min reward of 5, and a shrink_ratio of 0.9
        """

        super(Apple, self).__init__(initial_position=initial_position, default_config_key='apple', **kwargs)


# @EntityGenerator.register('rotten-apple')
class RottenApple(Edible):

    def __init__(self, initial_position, **kwargs):

        """ Edible entity that provides a positive reward

        Default: Brown Circle of radius 10, with an initial_reward of -30, a min reward of -5, and a shrink_ratio of 0.9
        """

        super(RottenApple, self).__init__(initial_position=initial_position, default_config_key='rotten_apple',
                                          **kwargs)


# @EntityGenerator.register('dispenser')
class Dispenser(Entity):

    entity_type = 'dispenser'
    interactive = True

    def __init__(self, initial_position, entity_produced, entity_produced_params=None, production_area=None, **kwargs):

        """ Dispenser Entity

        Dispenser entities produce a new entity in an area of the playground when activated.
        Default: pink circle of radius 15.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            entity_produced: Class of the entity produced by the dispenser
            entity_produced_params: Dictionary of additional parameters for the entity_produced
            production_area: PositionAreaSampler.
                If no production_area has been set, the entities will be produced around the dispenser.
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            production_limit: maximum number of entities produced. Default: 15

        """

        default_config = self.parse_configuration('interactive', 'dispenser')
        entity_params = {**default_config, **kwargs}

        super(Dispenser, self).__init__(initial_position=initial_position, **entity_params)

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

        self.production_limit = entity_params['production_limit']
        print(self.production_limit)
        self.produced_entities = []

    def activate(self):

        if self.local_dispenser:
            initial_position = self.location_sampler.sample([self.position[0], self.position[1]])
        else:
            initial_position = self.location_sampler.sample()

        obj = self.entity_produced(initial_position=initial_position, is_temporary_entity=True,
                                   **self.entity_produced_params)

        return obj

    def reset(self):

        self.produced_entities = []
        super().reset()


# @EntityGenerator.register('key')
class Key(Entity):

    entity_type = 'key'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """ Key entity to open chest

        Default: Grey hexagon of radius 8 and mass 5, movable

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'key')
        entity_params = {**default_config, **kwargs}

        super(Key, self).__init__(initial_position=initial_position, **entity_params)

        self.pm_visible_shape.collision_type = CollisionTypes.GEM


# @EntityGenerator.register('chest')
class Chest(Entity):

    entity_type = 'chest'
    interactive = True

    def __init__(self, initial_position, key, treasure, **kwargs):
        """ Chest Entity

        Chest entities can be open when in contact with corresponding Key entity, and deliver a treasure.
        When opened, Chest and key disappear.
        Default: Purple rectangle of size 20x30

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            key: Key entity
            treasure: Entity that is delivered when chest is opened
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'chest')
        entity_params = {**default_config, **kwargs}

        super(Chest, self).__init__(initial_position=initial_position, **entity_params)

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


# @EntityGenerator.register('coin')
class Coin(Entity):

    entity_type = 'coin'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """ Coins are used with a VendingMachine to get rewards.

        Default: Gold circle of radius 5 and mass 5.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'coin')
        entity_params = {**default_config, **kwargs}

        super(Coin, self).__init__(initial_position=initial_position, **entity_params)

        self.pm_visible_shape.collision_type = CollisionTypes.GEM


# @EntityGenerator.register('vending-machine')
class VendingMachine(Entity):

    entity_type = 'vending_machine'
    interactive = True

    def __init__(self, initial_position, **kwargs):
        """ Vending machine Entity

        When in contact with a coin, provide a reward to the agent closest to the coin.
        Default: Orange square of size 20, provides a reward of 10.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'vending_machine')
        entity_params = {**default_config, **kwargs}

        super(VendingMachine, self).__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params.get('reward')


# @EntityGenerator.register('door')
class Door(Entity):

    entity_type = 'door'

    def __init__(self, initial_position, **kwargs):
        """ Door that can be opened with a switch

        Default: Pale green door

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'door')
        entity_params = {**default_config, **kwargs}

        super(Door, self).__init__(initial_position=initial_position, **entity_params)

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


# @EntityGenerator.register('openclose-switch')
class OpenCloseSwitch(Entity):

    entity_type = 'switch'
    interactive = True

    def __init__(self, initial_position, door, **kwargs):
        """ Switch used to open and close a door

        Opens or close a door when activated by an agent.
        Default: Pale brown square of size 10.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            door: Door opened by the switch
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(OpenCloseSwitch, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door

    def activate(self):

        if self.door.opened:
            self.door.close_door()

        else:
            self.door.open_door()


# @EntityGenerator.register('timer-switch')
class TimerSwitch(Entity):

    entity_type = 'switch'
    interactive = True

    def __init__(self, initial_position, door, time_open, **kwargs):
        """ Switch used to open a door for a certain duration

        Opens a door for a certain amount of time when activated by an agent.
        If activated when door is still open, resets the timer.
        Default: Pale brown square of size 10.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            door: Door opened by the switch
            time_open: Timesteps during which door will stay open
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(TimerSwitch, self).__init__(initial_position=initial_position, **entity_params)

        self.activable = True

        self.door = door

        self.time_open = time_open
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


# @EntityGenerator.register('push-button')
class PushButton(Entity):
    entity_type = 'pushbutton'

    def __init__(self, initial_position, door, **kwargs):
        """ Push button used to open a door

        Opens a door when in contact with an agent.
        Default: Pale brown square of size 10.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            door: Door opened by the switch
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(PushButton, self).__init__(initial_position=initial_position, **entity_params)
        self.pm_visible_shape.collision_type = CollisionTypes.CONTACT

        self.door = door

    def activate(self):

        self.door.open_door()


# @EntityGenerator.register('lock')
class Lock(Entity):

    entity_type = 'lock'
    interactive = True

    def __init__(self, initial_position, door, key, **kwargs):
        """ Lock for a door, opens with a key

        Opens a door when in contact with the associated key.
        Default: pale green 10x10 square

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            door: Door opened by the lock
            key: key associated with the lock
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self.parse_configuration('interactive', 'lock')
        entity_params = {**default_config, **kwargs}

        super(Lock, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door
        self.key = key

    def activate(self):

        self.door.open_door()
