from ..entity import Entity
from ...utils import CollisionTypes, PositionAreaSampler
from ...agents.body_parts.parts import Part
from ...playgrounds.playground import Playground

from abc import ABC, abstractmethod


class InteractiveSceneElement(ABC, Entity):

    interactive = True

    def __init__(self, **kwargs):

        Entity.__init__(self, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

    @abstractmethod
    def activate(self, activating_entity):
        list_remove = []
        list_add = []

        return list_remove, list_add

    @property
    @abstractmethod
    def reward(self):
        ...

    @reward.setter
    @abstractmethod
    def reward(self, rew):
        ...


class Lever(InteractiveSceneElement):

    entity_type = 'lever'

    def __init__(self, initial_position, **kwargs):
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

        default_config = self._parse_configuration('interactive', 'lever')
        entity_params = {**default_config, **kwargs}

        super(Lever, self).__init__(initial_position=initial_position, **entity_params)

        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.reward = entity_params['reward']

        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    @property
    def reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def activate(self, _):
        return super().activate(_)


class Dispenser(InteractiveSceneElement):

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

        default_config = self._parse_configuration('interactive', 'dispenser')
        entity_params = {**default_config, **kwargs}

        super(Dispenser, self).__init__(initial_position=initial_position, **entity_params)

        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

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
        self.produced_entities = []

    @property
    def reward(self):
        return 0

    def activate(self, _):

        list_remove = []
        list_add = []

        if len(self.produced_entities) < self.production_limit:

            if self.local_dispenser:
                initial_position = self.location_sampler.sample([self.position[0], self.position[1]])
            else:
                initial_position = self.location_sampler.sample()

            obj = self.entity_produced(initial_position=initial_position, is_temporary_entity=True,
                                       **self.entity_produced_params)

            self.produced_entities.append(obj)
            list_add = [obj]

        return list_remove, list_add

    def reset(self):

        self.produced_entities = []
        super().reset()


class Chest(InteractiveSceneElement):

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

        default_config = self._parse_configuration('interactive', 'chest')
        entity_params = {**default_config, **kwargs}

        super(Chest, self).__init__(initial_position=initial_position, **entity_params)
        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.key = key
        self.treasure = treasure
        self.treasure.is_temporary_entity = True

    @property
    def reward(self):
        return 0

    def activate(self, key):

        list_remove = []
        list_add = []

        if key is self.key:

            self.treasure.initial_position = self.position

            list_remove = [self.key, self]
            list_add = [self.treasure]

        return list_remove, list_add


class VendingMachine(InteractiveSceneElement):

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

        default_config = self._parse_configuration('interactive', 'vending_machine')
        entity_params = {**default_config, **kwargs}

        super(VendingMachine, self).__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params.get('reward')

        self.accepted_coins = []

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def activate(self, coin):

        list_add = []
        list_remove = []

        if coin in self.accepted_coins.copy():
            list_remove = [coin]
            self.accepted_coins.remove(coin)

        return list_remove, list_add


class OpenCloseSwitch(InteractiveSceneElement):

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

        default_config = self._parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(OpenCloseSwitch, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door

    @property
    def reward(self):
        return 0

    def activate(self, _):

        list_add = []
        list_remove = []

        if self.door.opened:
            self.door.close_door()
            list_add = [self.door]

        else:
            self.door.open_door()
            list_remove = [self.door]

        return list_remove, list_add


class TimerSwitch(InteractiveSceneElement):

    entity_type = 'switch'
    timed = True

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

        default_config = self._parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(TimerSwitch, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door

        self.time_open = time_open
        self.timer = self.time_open

    @property
    def reward(self):
        return 0

    def activate(self, activating_entity):

        list_remove = []
        list_add = []

        if isinstance(activating_entity, Part):
            if not self.door.opened:
                self.door.open_door()
                list_remove = [self.door]

            self.reset_timer()

        if isinstance(activating_entity, Playground):
            self.door.close_door()
            list_add = [self.door]
            self.reset_timer()

        return list_remove, list_add

    def reset_timer(self):

        self.timer = self.time_open

    def update(self):

        if self.door.opened:
            self.timer -= 1

    def reset(self):

        self.timer = self.time_open
        self.door.close_door()


class Lock(InteractiveSceneElement):

    entity_type = 'lock'

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

        default_config = self._parse_configuration('interactive', 'lock')
        entity_params = {**default_config, **kwargs}

        super(Lock, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door
        self.key = key

    @property
    def reward(self):
        return 0

    def activate(self, key):

        list_add = []
        list_remove = []

        if key is self.key:
            self.door.open_door()

            list_remove = [self.door, self.key, self]

        return list_remove, list_add
