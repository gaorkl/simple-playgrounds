"""
Scene elements that interact with an agent when they are in range.
Passive Scene Elements do not require action from an agent.
"""
from abc import ABC

from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, SceneElementTypes
from simple_playgrounds.utils.parser import parse_configuration


class PassiveSceneElement(SceneElement, ABC):
    """
    Passive Scene Elements are activated when an agent is within
    their interaction radius.
    """

    interactive = True

    def __init__(self, **kwargs):
        SceneElement.__init__(self, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.PASSIVE

        self.reward = 0
        self.reward_provided = False

    def pre_step(self):
        super(PassiveSceneElement, self).pre_step()
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


class TerminationZone(PassiveSceneElement, ABC):
    """
    Termination Zones terminate the episode when activated.
    """

    terminate_upon_contact = True
    visible = False

    def __init__(self, **kwargs):
        """
        Base class for Invisible zones that terminate upon contact.

        TerminationZone entities generate a termination of the episode,
        and provide a reward to the agent in contact with the entity.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class.

        Keyword Args:
            reward: Reward provided.
        """

        default_config = parse_configuration('element_zone', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.reward = entity_params.get('reward', 0)
        self.reward_provided = False


class GoalZone(TerminationZone):
    """
    Termination Zone that provides positive reward when activated.
    """

    entity_type = SceneElementTypes.GOAL_ZONE


class DeathZone(TerminationZone):
    """
    Termination Zone that provides negative reward when activated.
    """

    entity_type = SceneElementTypes.DEATH_ZONE


class RewardZone(PassiveSceneElement, ABC):
    """
    Reward Zones provide a reward to an agent in the zone.
    """
    visible = False

    def __init__(self, **kwargs):
        """
        RewardZone entities are invisible zones.
        Provide a reward to the agent which is inside the zone.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in the zone
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = parse_configuration('element_zone', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.reward = entity_params['reward']

        self.initial_total_reward = entity_params['total_reward']
        self.total_reward = self.initial_total_reward

    @property
    def reward(self):

        if not self.reward_provided:
            self.reward_provided = True

            if self._reward * self.total_reward < 0:
                return 0

            self.total_reward -= self._reward
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def reset(self):
        self.total_reward = self.initial_total_reward
        super().reset()


class ToxicZone(RewardZone):
    """
    ToxicZone is an invisible entity.
    Provides a reward to an agent which is in the zone.

    Provides a negative reward for each timestep when an agent is in the zone.
    Default: Yellow square of radius 15, reward -1 and total_reward -1000000
    """

    entity_type = SceneElementTypes.TOXIC_ZONE


class HealingZone(RewardZone):

    """
    HealingZone is an invisible entity.
    Provides a reward to an agent which is in the zone.

    Provides a positive reward for each timestep when an agent is in the zone.
    Default: Blue square of radius 15, reward 1 and total_reward  100000

    """

    entity_type = SceneElementTypes.HEALING_ZONE
