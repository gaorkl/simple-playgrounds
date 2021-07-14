"""
Scene elements that interact with an agent when they are in range.
Passive Scene Elements do not require action from an agent.
"""
from typing import Optional

from abc import ABC

from ...elements.element import ZoneElement
from ...common.definitions import ElementTypes
from ...configs.parser import parse_configuration


class TerminationZone(ZoneElement, ABC):
    """
    Termination Zones terminate the episode when activated.
    """
    def __init__(self, config_key, **kwargs):
        """
        Base class for Invisible zones that terminate upon contact.

        TerminationZone entities generate a termination of the episode,
        and provide a reward to the agent in contact with the entity.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class.

        Keyword Args:
            reward: Reward provided.
        """

        default_config = parse_configuration('element_zone', config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

    @property
    def terminate_upon_activation(self):
        return True

    def activate(self, *args):
        return None, None


class GoalZone(TerminationZone):
    """
    Termination Zone that provides positive reward when activated.
    """
    def __init__(self, reward: float, **kwargs):

        assert reward > 0

        super().__init__(ElementTypes.GOAL_ZONE, reward=reward, **kwargs)


class DeathZone(TerminationZone):
    """
    Termination Zone that provides negative reward when activated.
    """
    def __init__(self, reward: float, **kwargs):

        assert reward < 0

        super().__init__(ElementTypes.DEATH_ZONE, reward=reward, **kwargs)


class RewardZone(ZoneElement, ABC):
    """
    Reward Zones provide a reward to an agent in the zone.
    """
    def __init__(self, config_key, reward: float, limit: Optional[float],
                 **entity_params):
        """
        RewardZone entities are invisible zones.
        Provide a reward to the agent which is inside the zone.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in the zone
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = parse_configuration('element_zone', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(reward=reward, **entity_params)

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


class ToxicZone(RewardZone):
    """
    ToxicZone is an invisible entity.
    Provides a reward to an agent which is in the zone.

    Provides a negative reward for each timestep when an agent is in the zone.
    Default: Yellow square of radius 15, reward -1 and total_reward -1000000
    """
    def __init__(
        self,
        reward: float,
        limit: Optional[float],
        **entity_params,
    ):

        assert reward < 0

        super().__init__(ElementTypes.TOXIC_ZONE,
                         reward=reward,
                         limit=limit,
                         **entity_params)


class HealingZone(RewardZone):
    """
    HealingZone is an invisible entity.
    Provides a reward to an agent which is in the zone.

    Provides a positive reward for each timestep when an agent is in the zone.
    Default: Blue square of radius 15, reward 1 and total_reward  100000

    """
    def __init__(
        self,
        reward: float,
        limit: Optional[float],
        **entity_params,
    ):
        assert reward > 0

        super().__init__(ElementTypes.HEALING_ZONE,
                         reward=reward,
                         limit=limit,
                         **entity_params)
