"""
InteractiveSceneElements can be activated by an agent.
"""
from abc import ABC, abstractmethod

from simple_playgrounds.agents.parts.parts import Part
from simple_playgrounds.playground import Playground
from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, SceneElementTypes
from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.playgrounds.scene_elements.elements.gem import Coin

# pylint: disable=line-too-long


class InteractiveSceneElement(SceneElement, ABC):
    """Base Class dor InteractiveSceneElements"""
    interactive = True

    def __init__(self, **kwargs):
        SceneElement.__init__(self, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.activated = False

    @abstractmethod
    def activate(self, activating_entity):
        """
        Activate the SceneElement.

        Args:
            activating_entity: Entity that activated the SceneElement.

        Returns:
            A tuple (entity_removed, entity_added).
             entity_added can be:
              - an entity, in which case playground will assume that it was already placed before and has a position.
              - a tuple (entity, position).
              - None
             entity_removed can be:
              - an entity
              - a list of entities
              - None

        """
        return None, None

    @property
    @abstractmethod
    def reward(self):
        """Reward provided upon activation."""
        ...

    @reward.setter
    @abstractmethod
    def reward(self, rew):
        ...

    def pre_step(self):
        self.activated = False


class Lever(InteractiveSceneElement):
    """Lever Entities provide a reward when activated."""

    entity_type = SceneElementTypes.LEVER

    def __init__(self, **kwargs):

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.reward = entity_params['reward']

        self.reward_provided = False

    def pre_step(self):
        super().pre_step()
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

    def activate(self, activating_entity):
        # pylint: disable=useless-super-delegation
        return super().activate(activating_entity)


class Dispenser(InteractiveSceneElement):
    """Dispenser produces a new entity in an area of the playground when activated.
    """

    entity_type = SceneElementTypes.DISPENSER
    interactive = True

    def __init__(self, entity_produced, entity_produced_params=None, production_area=None, **kwargs):

        """
        Default: pink circle of radius 15.

        Args:
            entity_produced: Class of the entity produced by the dispenser.
            entity_produced_params: Dictionary of additional parameters for the entity_produced.
            production_area: PositionAreaSampler.
                If no production_area has been set, the entities will be produced around the dispenser.
            **kwargs: other params to configure entity. Refer to Entity class.

        Keyword Args:
            production_limit: maximum number of entities produced. Default: 15.
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.entity_produced = entity_produced

        if entity_produced_params is None:
            self.entity_produced_params = {}
        else:
            self.entity_produced_params = entity_produced_params

        if production_area is None:
            self.local_dispenser = True
            self.location_sampler = CoordinateSampler(area_shape='circle',
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

        elem_add = None

        if len(self.produced_entities) < self.production_limit and self.activated is False:

            if self.local_dispenser:
                initial_coordinate = self.location_sampler.sample(self.position)
            else:
                initial_coordinate = self.location_sampler.sample()

            obj = self.entity_produced(is_temporary_entity=True,
                                       **self.entity_produced_params)

            self.produced_entities.append(obj)
            elem_add = (obj, initial_coordinate)

            self.activated = True

        return None, elem_add

    def reset(self):

        self.produced_entities = []
        super().reset()


class Chest(InteractiveSceneElement):

    """
    Chest can be open when in contact with corresponding Key entity, and deliver a treasure.
    When opened, Chest and key disappear, treasure appears.
    """

    entity_type = SceneElementTypes.CHEST
    interactive = True
    background = False

    def __init__(self, key, treasure, **kwargs):
        """ Chest Entity.
        Default: Purple rectangle of size 20x30

        Args:
            key: Key object.
            treasure: SceneElement that is delivered when chest is opened.
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)
        self.pm_interaction_shape.collision_type = CollisionTypes.ACTIVATED_BY_GEM

        self.key = key
        self.treasure = treasure
        self.treasure.is_temporary_entity = True

    @property
    def reward(self):
        return 0

    def activate(self, activating_entity):

        list_remove = None
        elem_add = None

        if activating_entity is self.key:

            list_remove = [self.key, self]
            elem_add = (self.treasure, self.coordinates)

        return list_remove, elem_add


class VendingMachine(InteractiveSceneElement):

    """
    When in contact with a coin, provide a reward to the agent closest to the coin.
    """

    entity_type = SceneElementTypes.VENDING_MACHINE
    interactive = True

    def __init__(self, **kwargs):
        """ Vending machine Entity.
        Default: Orange square of size 20, provides a reward of 10.
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)
        self.pm_interaction_shape.collision_type = CollisionTypes.ACTIVATED_BY_GEM

        self.reward = entity_params.get('reward')

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def activate(self, activating_entity):

        list_remove = None

        if isinstance(activating_entity, Coin) and activating_entity.vending_machine is self:
            list_remove = [activating_entity]
            self.activated = True

        return list_remove, None


class OpenCloseSwitch(InteractiveSceneElement):

    """
    Opens or close a door when activated by an agent.
    """

    entity_type = SceneElementTypes.SWITCH
    interactive = True

    def __init__(self, door, **kwargs):
        """ Switch used to open and close a door

        Default: Pale brown square of size 10.

        Args:
            door: Door opened by the switch.
            **kwargs: other params to configure entity. Refer to Entity class.

        Notes:
            It is possible to have multiple switches for a single door.
            However the behavior is unstable in multiagent setting.
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.door = door

    @property
    def reward(self):
        return 0

    def activate(self, _):

        elem_add = None
        elem_remove = None

        if self.activated is False:
            if self.door.opened:
                self.door.opened = False
                elem_add = self.door

            else:
                self.door.opened = True
                elem_remove = self.door

            self.activated = True

        return elem_remove, elem_add


class TimerSwitch(InteractiveSceneElement):

    """
    Opens a door for a certain amount of time when activated by an agent.
    If activated when door is still open, resets the timer.
    """

    entity_type = SceneElementTypes.SWITCH
    timed = True

    def __init__(self, door, time_open, **kwargs):
        """ Switch used to open a door for a certain duration.

        Default: Pale brown square of size 10.

        Args:
            door: Door opened by the switch.
            time_open: Timesteps during which door will stay open.
            **kwargs: other params to configure entity. Refer to Entity class.
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.door = door

        self.time_open = time_open
        self.timer = self.time_open

    @property
    def reward(self):
        return 0

    def activate(self, activating_entity):

        elem_remove = None
        elem_add = None

        if isinstance(activating_entity, Part) and self.activated is False:
            if not self.door.opened:
                self.door.opened = True
                elem_remove = self.door

            self._reset_timer()
            self.activated = True

        if isinstance(activating_entity, Playground):
            self.door.opened = False
            elem_add = self.door
            self._reset_timer()

        return elem_remove, elem_add

    def _reset_timer(self):

        self.timer = self.time_open

    def pre_step(self):

        self.activated = False
        if self.door.opened:
            self.timer -= 1

    def reset(self):

        self.timer = self.time_open
        self.door.opened = False


class Lock(InteractiveSceneElement):

    """
    Opens a door when in contact with the associated key.
    """
    entity_type = SceneElementTypes.LOCK
    background = False

    def __init__(self, door, key, **kwargs):
        """ Lock for a door, opens with a key.

        Default: pale green 10x10 square.

        Args:
            door: Door opened by the lock
            key: Key object associated with the lock
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__( **entity_params)
        self.pm_interaction_shape.collision_type = CollisionTypes.ACTIVATED_BY_GEM

        self.door = door
        self.key = key

    @property
    def reward(self):
        return 0

    def activate(self, activating_entity):

        list_remove = None

        if activating_entity is self.key:
            self.door.opened = True

            list_remove = [self.door, self.key, self]

        return list_remove, None
