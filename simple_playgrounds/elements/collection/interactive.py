"""
InteractiveSceneElements can be activated by an agent.
"""
from typing import Dict, Optional
from abc import ABC

from simple_playgrounds.elements.element import InteractiveElement, SceneElement, GemElement

# from simple_playgrounds.playground import Playground
# from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.common.position_samplers import CoordinateSampler
from simple_playgrounds.configs import parse_configuration

# from simple_playgrounds.playgrounds.scene_elements.elements.gem import Coin

# pylint: disable=line-too-long


class ActivableElement(InteractiveElement, ABC):

    def __init__(self, config_key, **entity_params):

        default_config = parse_configuration('element_interactive', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(visible_shape=True, invisible_shape=True, **entity_params)

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.ACTIVABLE

    @property
    def terminate_upon_activation(self):
        return False


class Dispenser(ActivableElement):
    """Dispenser produces a new entity in an area of the playground when activated.
    """

    def __init__(self,
                 element_produced: SceneElement.__class__,
                 element_produced_params: Optional[Dict],
                 production_area: Optional[CoordinateSampler],
                 production_limit: Optional[int],
                 production_range: Optional[float],
                 **entity_params):

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

        super().__init__(config_key=ElementTypes.DISPENSER, **entity_params)

        self.elem_class_produced = element_produced

        if element_produced_params is None:
            element_produced_params = {}
        self.element_produced_params = element_produced_params

        if production_area:
            self._coordinates_sampler = production_area

        else:
            self._coordinates_sampler = CoordinateSampler(area_shape='circle',
                                                          center=self,
                                                          radius=self._radius_visible + production_range,
                                                          excl_radius=self._radius_visible)

        self.production_limit = production_limit
        self.produced_entities = []

    def activate(self):

        elem_add = None

        if len(self.produced_entities) < self.production_limit:

            initial_coordinate = self._coordinates_sampler.sample()
            elem = self.elem_class_produced(is_temporary_entity=True,
                                            **self.element_produced_params)

            self.produced_entities.append(elem)
            elem_add = (elem, initial_coordinate)

        return None, elem_add

    def reset(self):

        self.produced_entities = []
        super().reset()


class ActivableByGem(ActivableElement, ABC):

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.ACTIVABLE_BY_GEM


class VendingMachine(ActivableByGem):
    """
    When in contact with a coin, provide a reward to the agent closest to the coin.
    """

    def __init__(self,
                 reward: float,
                 limit: Optional[int],
                 **entity_params,
                 ):
        """ Vending machine Entity.
        Default: Orange square of size 20, provides a reward of 10.
        """

        super().__init__(ElementTypes.VENDING_MACHINE, reward=reward, **entity_params)
        self._limit = limit
        self._total_reward_provided = 0

    def activate(self,
                 activating: GemElement,
                 ):
        list_remove = None

        if activating.elem_activated is self:
            self.activated = True
            list_remove = activating

        return list_remove, None

    @property
    def reward(self):
        rew = super().reward

        if self._limit and self._total_reward_provided > self._limit:
            return 0

        self._total_reward_provided += rew
        return rew

    @reward.setter
    def reward(self, rew: float):
        self._reward = rew

    def reset(self):
        super().reset()
        self._total_reward_provided = 0


class Chest(ActivableByGem):

    """
    Chest can be open when in contact with corresponding Key entity, and deliver a treasure.
    When opened, Chest and key disappear, treasure appears.
    """

    def __init__(self,
                 treasure: SceneElement,
                 **entity_params):

        """ Chest Entity.
        Default: Purple rectangle of size 20x30

        Args:
            key: Key object.
            treasure: SceneElement that is delivered when chest is opened.
            **kwargs: other params to configure entity. Refer to Entity class
        """

        super().__init__(ElementTypes.CHEST, reward=0, **entity_params)

        self.treasure = treasure
        self.treasure.is_temporary_entity = True

    def activate(self,
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

    def __init__(self, door, **kwargs):
        """ Lock for a door, opens with a key.

        Default: pale green 10x10 square.

        Args:
            door: Door opened by the lock
            key: Key object associated with the lock
            **kwargs: other params to configure entity. Refer to Entity class
        """

        super().__init__( ElementTypes.LOCK, **kwargs)

        self.door = door

    def activate(self,
                 activating: GemElement,
                 ):

        list_remove = None

        if activating.elem_activated is self:

            self.door.opened = True
            list_remove = [activating, self]

        return list_remove, None


# class Lever(InteractiveSceneElement):
#     """Lever Entities provide a reward when activated."""
#
#     entity_type = SceneElementTypes.LEVER
#
#     def __init__(self, **kwargs):
#
#         default_config = parse_configuration('element_interactive', self.entity_type)
#         entity_params = {**default_config, **kwargs}
#
#         super().__init__(**entity_params)
#
#         self.pm_interaction_shape.collision_type = CollisionTypes.ACTIVABLE
#
#         self.reward = entity_params['reward']
#
#         self.reward_provided = False
#
#     def pre_step(self):
#         super().pre_step()
#         self.reward_provided = False
#
#     @property
#     def reward(self):
#
#         if not self.reward_provided:
#             self.reward_provided = True
#             return self._reward
#
#         return 0
#
#     @reward.setter
#     def reward(self, rew):
#         self._reward = rew
#
#     def activate(self, activating_entity):
#         # pylint: disable=useless-super-delegation
#         return super().activate(activating_entity)
#

#

#
#

#
# class OpenCloseSwitch(InteractiveSceneElement):
#
#     """
#     Opens or close a door when activated by an agent.
#     """
#
#     entity_type = SceneElementTypes.SWITCH
#     interactive = True
#
#     def __init__(self, door, **kwargs):
#         """ Switch used to open and close a door
#
#         Default: Pale brown square of size 10.
#
#         Args:
#             door: Door opened by the switch.
#             **kwargs: other params to configure entity. Refer to Entity class.
#
#         Notes:
#             It is possible to have multiple switches for a single door.
#             However the behavior is unstable in multiagent setting.
#         """
#
#         default_config = parse_configuration('element_interactive', self.entity_type)
#         entity_params = {**default_config, **kwargs}
#
#         super().__init__(**entity_params)
#
#         self.door = door
#
#     @property
#     def reward(self):
#         return 0
#
#     def activate(self, _):
#
#         elem_add = None
#         elem_remove = None
#
#         if self.activated is False:
#             if self.door.opened:
#                 self.door.opened = False
#                 elem_add = self.door
#
#             else:
#                 self.door.opened = True
#                 elem_remove = self.door
#
#             self.activated = True
#
#         return elem_remove, elem_add

#
# class TimerSwitch(InteractiveSceneElement):
#
#     """
#     Opens a door for a certain amount of time when activated by an agent.
#     If activated when door is still open, resets the timer.
#     """
#
#     entity_type = SceneElementTypes.SWITCH
#     timed = True
#
#     def __init__(self, door, time_open, **kwargs):
#         """ Switch used to open a door for a certain duration.
#
#         Default: Pale brown square of size 10.
#
#         Args:
#             door: Door opened by the switch.
#             time_open: Timesteps during which door will stay open.
#             **kwargs: other params to configure entity. Refer to Entity class.
#         """
#
#         default_config = parse_configuration('element_interactive', self.entity_type)
#         entity_params = {**default_config, **kwargs}
#
#         super().__init__(**entity_params)
#
#         self.door = door
#
#         self.time_open = time_open
#         self.timer = self.time_open
#
#     @property
#     def reward(self):
#         return 0
#
#     def activate(self, activating_entity):
#
#         elem_remove = None
#         elem_add = None
#
#         if isinstance(activating_entity, Part) and self.activated is False:
#             if not self.door.opened:
#                 self.door.opened = True
#                 elem_remove = self.door
#
#             self._reset_timer()
#             self.activated = True
#
#         if isinstance(activating_entity, Playground):
#             self.door.opened = False
#             elem_add = self.door
#             self._reset_timer()
#
#         return elem_remove, elem_add
#
#     def _reset_timer(self):
#
#         self.timer = self.time_open
#
#     def pre_step(self):
#
#         self.activated = False
#         if self.door.opened:
#             self.timer -= 1
#
#     def reset(self):
#
#         self.timer = self.time_open
#         self.door.opened = False


#
