from abc import ABC
from simple_playgrounds.playgrounds.scene_elements.elements.passive import PassiveSceneElement
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import SceneElementTypes


class VisibleRewardZone(PassiveSceneElement, ABC):
    """
    Base class for entities that provide reward to an agent in its proximity.
    """
    interactive = True

    def __init__(self, **kwargs):
        """
        VisibleRewardZone entities provide a reward to the agent
        in close proximity with the entity.

        Args:
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in proximity
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = parse_configuration('element_proximity', self.entity_type)
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

        self.reward_provided = False
        self.total_reward = self.initial_total_reward

        super().reset()


class Fairy(VisibleRewardZone):
    """
    Fairy entities provide a reward to an agent which is in proximity.

    Provides a positive reward of 2 for each timestep when an agent is in proximity.
    Default: Turquoise-blue circle of radius 8, reward 2 and total_reward 200.

    """
    entity_type = SceneElementTypes.FAIRY


class Fireball(VisibleRewardZone):
    """
    Fireball entities provide a negative reward to an agent which is in proximity.

    Provides a negative reward of 2 for each timestep when an agent is in proximity.
    Default: Red circle of radius 8, reward -2 and total_reward -200.

    """

    entity_type = SceneElementTypes.FIREBALL
