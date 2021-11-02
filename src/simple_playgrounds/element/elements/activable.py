"""
InteractiveSceneElements can be activated by an agent.
"""
from __future__ import annotations

from typing import Dict, Optional, Union, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.element.elements.gem import GemElement

from abc import ABC

from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.common.timer import Timer, CountDownTimer
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.configs.parser import parse_configuration

from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.element.elements.basic import Door
from simple_playgrounds.element.element import SceneElement, InteractiveElement


# pylint: disable=line-too-long


class ActivableElement(InteractiveElement, ABC):
    def __init__(self,
                 config_key: Optional[Union[ElementTypes, str]] = None,
                 **kwargs):

        default_config = parse_configuration('element_activable', config_key)
        kwargs = {**default_config, **kwargs}

        super().__init__(visible_shape=True, invisible_shape=True, **kwargs)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.ACTIVABLE

    @property
    def terminate_upon_activation(self):
        return False


class ActivableByGem(ActivableElement, ABC):
    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.ACTIVABLE_BY_GEM


class Dispenser(ActivableElement):
    """Dispenser produces a new entity in an area of the playground when activated.
    """
    def __init__(self,
                 element_produced: Type[SceneElement],
                 element_produced_params: Optional[Dict] = None,
                 production_limit: Optional[int] = None,
                 production_area: Optional[Union[SceneElement,
                                                 CoordinateSampler]] = None,
                 production_range: Optional[float] = None,
                 **kwargs):
        """
        Default: pink circle of radius 15.

        Args:
            element_produced: Class of the entity produced by the dispenser.
            element_produced_params: Dictionary of additional parameters for the entity_produced.
            production_area: PositionAreaSampler.
                If no production_area has been set, the entities will be produced around the dispenser.
            **kwargs: other params to configure entity. Refer to Entity class.

        Keyword Args:
            production_limit: maximum number of entities produced. Default: 15.
        """

        super().__init__(config_key=ElementTypes.DISPENSER, **kwargs)

        self.elem_class_produced = element_produced

        if not element_produced_params:
            element_produced_params = {}
        self.element_produced_params = element_produced_params

        self._recompute_center = False
        self._center_elem = None

        if not production_area:
            production_area = self

        if isinstance(production_area, SceneElement):

            assert production_range
            self._recompute_center = True
            self._center_elem = production_area

            radius = production_area.radius + production_range
            min_radius = production_area.radius

            self._coordinates_sampler = CoordinateSampler(
                area_shape='circle',
                center=(0, 0),
                radius=radius,
                min_radius=min_radius)

        else:
            assert isinstance(production_area, CoordinateSampler)
            self._coordinates_sampler = production_area

        self.production_limit = production_limit
        self.produced_entities: List[SceneElement] = []

    def activate(self, _):

        elem_add = None

        if not self.production_limit or len(
                self.produced_entities) < self.production_limit:

            self.activated = True

            if self._recompute_center:
                initial_coordinate = self._coordinates_sampler.sample(
                    self._center_elem.coordinates)
            else:
                initial_coordinate = self._coordinates_sampler.sample()
            elem = self.elem_class_produced(temporary=True,
                                            **self.element_produced_params)

            self.produced_entities.append(elem)
            elem_add = [(elem, initial_coordinate)]

        return None, elem_add

    def reset(self):

        self.produced_entities = []
        super().reset()


class RewardOnActivation(ActivableElement):
    """Fountain provides a reward when activated."""
    def __init__(
        self,
        reward: float,
        quantity_rewards: Optional[int] = None,
        **kwargs,
    ):

        super().__init__(reward=reward,
                         config_key=ElementTypes.REWARD_ON_ACTIVATION,
                         **kwargs)

        self._quantity_rewards = quantity_rewards
        self._count_rewards = 0

    @property
    def reward(self):
        rew = super().reward

        if self._quantity_rewards and self._count_rewards >= self._quantity_rewards:
            return 0

        self._count_rewards += 1
        return rew

    @reward.setter
    def reward(self, rew: float):
        self._reward = rew

    def activate(self, _):
        return None, None

    def reset(self):
        super().reset()
        self._count_rewards = 0


class OpenCloseSwitch(ActivableElement):
    """
    Opens or close a door when activated by an agent.
    """
    def __init__(
        self,
        door: Door,
        **kwargs,
    ):
        """ Switch used to open and close a door

        Default: Pale brown square of size 10.

        Args:
            door: Door opened by the switch.
            **kwargs: other params to configure entity. Refer to Entity class.

        Notes:
            It is possible to have multiple switches for a single door.
            However the behavior is unstable in multiagent setting.
        """

        super().__init__(reward=0, config_key=ElementTypes.SWITCH, **kwargs)

        self.door = door

    def activate(self, activator: Union[Timer, Agent]):

        elem_add = None
        elem_remove = None

        if self.door.opened:
            self.door.close()
            elem_add = [(self.door, None)]

        else:
            self.door.open()
            elem_remove = [self.door]

        self.activated = True

        return elem_remove, elem_add


class TimerSwitch(OpenCloseSwitch):
    """
    Opens a door for a certain amount of time when activated by an agent.
    If activated when door is still open, resets the timer.
    """
    def __init__(
        self,
        door: Door,
        timer: CountDownTimer,
        **kwargs,
    ):
        """ Switch used to open a door for a certain duration.

        Default: Pale brown square of size 10.

        Args:
            door: Door opened by the switch.
            time_open: Timesteps during which door will stay open.
            **kwargs: other params to configure entity. Refer to Entity class.
        """

        super().__init__(door=door, **kwargs)

        self._timer = timer

    def activate(self, activator: Union[Timer, Agent]):

        elem_remove = None
        elem_add = None

        if isinstance(activator, Timer):

            assert activator is self._timer

            self._timer.stop()
            self._timer.reset()

            if self.door.opened:
                self.door.close()
                elem_add = [(self.door, None)]

        elif isinstance(activator, Agent):

            self._timer.reset()
            self._timer.start()
            if not self.door.opened:
                self.door.open()
                elem_remove = [self.door]

        self.activated = True

        return elem_remove, elem_add


class VendingMachine(ActivableByGem):
    """
    When in contact with a coin, provide a reward to the agent closest to the coin.
    """
    def __init__(
        self,
        reward: float,
        quantity_rewards: Optional[int] = None,
        **kwargs,
    ):
        """ Vending machine Entity.
        Default: Orange square of size 20, provides a reward of 10.
        """

        super().__init__(ElementTypes.VENDING_MACHINE, reward=reward, **kwargs)
        self._quantity_rewards = quantity_rewards
        self._count_rewards = 0

    def activate(
        self,
        activating: GemElement,
    ):
        list_remove = None

        if activating.elem_activated:
            list_remove = [activating]

        return list_remove, None

    @property
    def reward(self):
        rew = super().reward

        if self._quantity_rewards and self._count_rewards >= self._quantity_rewards:
            return 0

        self._count_rewards += 1
        return rew

    @reward.setter
    def reward(self, rew: float):
        self._reward = rew

    def reset(self):
        super().reset()
        self._count_rewards = 0


class Chest(ActivableByGem):
    """
    Chest can be open when in contact with corresponding Key entity, and deliver a treasure.
    When opened, Chest and key disappear, treasure appears.
    """
    def __init__(
        self,
        treasure: SceneElement,
        **kwargs,
    ):
        """ Chest Entity.
        Default: Purple rectangle of size 20x30

        Args:
            key: Key object.
            treasure: SceneElement that is delivered when chest is opened.
            **kwargs: other params to configure entity. Refer to Entity class
        """

        super().__init__(ElementTypes.CHEST, reward=0, **kwargs)

        self.treasure = treasure
        self.treasure.temporary = True

    def activate(
        self,
        activating: GemElement,
    ):

        list_remove = None
        elem_add = None

        if activating.elem_activated is self:
            list_remove = [activating, self]
            elem_add = [(self.treasure, self.coordinates)]

        return list_remove, elem_add


class Lock(ActivableByGem):
    """
    Opens a door when in contact with the associated key.
    """
    def __init__(
        self,
        door: Door,
        **kwargs,
    ):
        """ Lock for a door, opens with a key.

        Default: pale green 10x10 square.

        Args:
            door: Door opened by the lock
            key: Key object associated with the lock
            **kwargs: other params to configure entity. Refer to Entity class
        """

        super().__init__(ElementTypes.LOCK, **kwargs)

        self.door = door

    def activate(
        self,
        activating: GemElement,
    ):

        list_remove = None

        if activating.elem_activated is self:
            self.door.open()
            list_remove = [self.door, self, activating]

        return list_remove, None
