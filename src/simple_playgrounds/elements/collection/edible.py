"""
Module for Edible SceneElement
"""
from abc import ABC
from typing import Optional, Union

from ..element import InteractiveElement
from ...common.definitions import ElementTypes, CollisionTypes
from ...configs.parser import parse_configuration


# pylint: disable=line-too-long


class Edible(InteractiveElement, ABC):
    """
    Base class for edible Scene Elements.
    Once eaten by an agent, the SceneElement shrinks in size, mass, and available reward.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 reward: float,
                 shrink_ratio: float,
                 min_reward: float,
                 config_key: Optional[Union[ElementTypes, str]] = None,
                 **entity_params):
        """
        Edible entity provides a reward to the agent that eats it, then shrinks in size, mass, and available reward.

        Args:
            **entity_params: other params to configure SceneElement. Refer to Entity class.

        Keyword Args:
            shrink_ratio_when_eaten: When eaten by an agent, the mass, size, and reward are multiplied by this ratio.
                Default: 0.9
            initial_reward: Initial reward of the edible.
            min_reward: When reward is lower than min_reward, the edible entity disappears.

        """

        default_config = parse_configuration('element_activable', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(visible_shape=True,
                         invisible_shape=True,
                         reward=reward,
                         **entity_params)

        self._entity_params = entity_params

        self._shrink_ratio = shrink_ratio
        self._min_reward = min_reward

    def activate(self, _):

        super().activate(_)

        # Change reward, size and mass
        prev_coordinates = self.coordinates

        new_reward = self._reward * self._shrink_ratio
        new_mass = self.mass * self._shrink_ratio
        new_radius = self._radius_visible * self._shrink_ratio

        continue_eating = False

        if self._reward > 0 and new_reward >= self._min_reward:
            continue_eating = True

        if self._reward < 0 and new_reward <= self._min_reward:
            continue_eating = True

        if continue_eating:

            entity_params = {
                **self._entity_params,
                'radius': new_radius,
                'reward': new_reward,
                'shrink_ratio': self._shrink_ratio,
                'min_reward': self._min_reward,
                'mass': new_mass,
                'texture': self.texture,
                'generate_texture': False,
                'temporary': True,
            }

            new_edible = self.__class__(**entity_params)

            new_edible.activated = True

            elem_add = [(new_edible, prev_coordinates)]
        else:
            elem_add = None

        return [self], elem_add

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.ACTIVABLE

    @property
    def terminate_upon_activation(self):
        return False


class Apple(Edible):
    """ Edible entity that provides a positive reward

    Default: Green Circle of radius 10, with an initial_reward of 30,
    a min reward of 5, and a shrink_ratio of 0.9.
    """
    def __init__(
        self,
        reward: float = 30,
        min_reward: float = 2,
        shrink_ratio: float = 0.9,
        **entity_params,
    ):

        assert reward >= min_reward >= 0

        super().__init__(config_key=ElementTypes.APPLE,
                         reward=reward,
                         shrink_ratio=shrink_ratio,
                         min_reward=min_reward,
                         **entity_params)


class RottenApple(Edible):
    """ Edible entity that provides a positive reward

    Default: Green Circle of radius 10, with an initial_reward of 30,
    a min reward of 5, and a shrink_ratio of 0.9.
    """
    def __init__(
        self,
        reward: float,
        min_reward: float,
        shrink_ratio: float = 0.9,
        **entity_params,
    ):
        assert reward <= min_reward <= 0

        super().__init__(config_key=ElementTypes.ROTTEN_APPLE,
                         reward=reward,
                         shrink_ratio=shrink_ratio,
                         min_reward=min_reward,
                         **entity_params)
