"""
Module for Edible SceneElement
"""
from abc import ABC
from simple_playgrounds.utils.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long

class Edible(InteractiveElement, ABC):
    """
    Base class for edible Scene Elements.
    Once eaten by an agent, the SceneElement shrinks in size, mass, and available reward.
    """

    # pylint: disable=too-many-instance-attributes

    interactive = True
    background = False

    def __init__(self,
                 reward: float,
                 shrink_ratio_when_eaten: float,
                 min_reward: float,
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

        default_config = parse_configuration('element_interactive', self.element_type)
        entity_params = {**default_config, **entity_params}

        super().__init__(reward=reward, **entity_params)

        self._shrink_ratio_when_eaten = shrink_ratio_when_eaten
        self._min_reward = min_reward

        self.initial_width, self.initial_length = self.width, self.length
        self.initial_radius = self.radius
        self.initial_mass = self.mass

        self.initial_reward = reward

    def assign_collision_to_shape(self):
        self.pm_interaction_shape.collision_type = CollisionTypes.EDIBLE

    def _generate_shapes_and_masks(self):

        self.pm_visible_shape = self._create_pm_shape()
        self.visible_mask = self._create_mask()

        self.pm_interaction_shape = self._create_pm_shape(is_interactive=True)
        self.pm_interaction_shape.collision_type = CollisionTypes.EDIBLE
        self.interaction_mask = self._create_mask(is_interactive=True)

        self.pm_elements = [self.pm_body, self.pm_visible_shape, self.pm_interaction_shape]

        if self.graspable:
            self.pm_grasp_shape = self._create_pm_shape(is_interactive=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.grasp_mask = self._create_mask(is_interactive=True)
            self.pm_elements.append(self.pm_grasp_shape)

    def activate(self,
                 entity: Union[None, Entity] = None,
                 ) -> AddRemoveElems:

        """" Change size, reward, and appearance."""
        # Change reward, size and mass
        previous_position = self.pm_body.position
        previous_angle = self.pm_body.angle

        self.reward = self.reward * self._shrink_ratio_when_eaten

        if self.movable:
            self.mass = self.mass * self._shrink_ratio_when_eaten

        self.pm_body = self._create_pm_body()
        # self.pm_elements = [self.pm_body]

        self.width = self.width * self._shrink_ratio_when_eaten
        self.length = self.length * self._shrink_ratio_when_eaten
        self.radius = self.radius * self._shrink_ratio_when_eaten
        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range

        self.pm_body.position = previous_position
        self.pm_body.angle = previous_angle

        self._generate_shapes_and_masks()

        continue_eating = False

        if self.initial_reward > 0 and self.reward > self._min_reward:
            continue_eating = True

        if self.initial_reward < 0 and self.reward < self._min_reward:
            continue_eating = True

        if continue_eating:
            elem_add = (self, None)
        else:
            elem_add = True

        return (self,), elem_add

    def reset(self):

        # pylint: disable=unused-argument

        self.reward = self.initial_reward
        self.mass = self.initial_mass

        self.width, self.length = self.initial_width, self.initial_length
        self.radius = self.initial_radius

        self.interaction_width = self.width + self.interaction_range
        self.interaction_length = self.length + self.interaction_range
        self.interaction_radius = self.radius + self.interaction_range

        self.pm_body = self._create_pm_body()

        super().reset()

        self._generate_shapes_and_masks()


class Apple(Edible):

    """ Edible entity that provides a positive reward

    Default: Green Circle of radius 10, with an initial_reward of 30,
    a min reward of 5, and a shrink_ratio of 0.9.
    """

    entity_type = ElementTypes.APPLE


class RottenApple(Edible):

    """ Edible entity that provides a negative reward

    Default: Brown Circle of radius 10, with an initial_reward of -30,
    a min reward of -5, and a shrink_ratio of 0.9.

    """
    entity_type = ElementTypes.ROTTEN_APPLE
