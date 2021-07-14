from typing import Optional

from abc import ABC
from ..element import InteractiveElement
from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from ...configs.parser import parse_configuration


class VisibleRewardZone(InteractiveElement, ABC):
    """
    Base class for entities that provide reward to an agent in its proximity.
    """

    def __init__(self, config_key: ElementTypes, reward: float, limit: Optional[float]=None,
                 **entity_params):
        """
        VisibleRewardZone entities provide a reward to the agent
        in close proximity with the entity.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in proximity
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = parse_configuration('element_proximity', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(visible_shape=True, invisible_shape=True, reward=reward, **entity_params)

        self._limit = limit
        self._total_reward_provided = 0

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
        self._total_reward_provided = 0
        super().reset()

    @property
    def terminate_upon_activation(self):
        return False

    def activate(self, *args):
        return None, None

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.CONTACT


class Fairy(VisibleRewardZone):
    """
    Fairy entities provide a reward to an agent which is in proximity.

    Provides a positive reward of 2 for each timestep when an agent is in proximity.
    Default: Turquoise-blue circle of radius 8, reward 2 and total_reward 200.

    """

    def __init__(self,  reward: float, limit: Optional[float]=None,
                 **entity_params):

        super().__init__(config_key=ElementTypes.FAIRY, reward = reward, limit=limit, **entity_params)


class Fireball(VisibleRewardZone):
    """
    Fireball entities provide a negative reward to an agent which is in proximity.

    Provides a negative reward of 2 for each timestep when an agent is in proximity.
    Default: Red circle of radius 8, reward -2 and total_reward -200.

    """

    def __init__(self, reward: float, limit: Optional[float] = None,
                 **entity_params):
        super().__init__(config_key=ElementTypes.FIREBALL, reward=reward, limit=limit, **entity_params)
