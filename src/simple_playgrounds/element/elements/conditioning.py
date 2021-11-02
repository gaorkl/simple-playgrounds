"""
Scene Elements used for conditioning experiments
"""
import random
from typing import List, Union, Dict, Tuple

from simple_playgrounds.element.element import InteractiveElement
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.common.texture import Texture, TextureGenerator, ColorTexture
from simple_playgrounds.common.timer import Timer
from simple_playgrounds.configs.parser import parse_configuration


class ColorChanging(InteractiveElement):
    """ SceneElement that changes its texture when activated."""
    def __init__(
        self,
        textures: List[Union[Texture, Dict, Tuple[int, int, int]]],
        mode: str = 'loop',
        activable_by_agent: bool = False,
        **kwargs,
    ):

        entity_params = parse_configuration(
            'element_conditioning', config_key=ElementTypes.COLOR_CHANGING)
        entity_params = {**kwargs, **entity_params}

        self.textures = []
        self._activable_by_agent = activable_by_agent

        super().__init__(visible_shape=True,
                         invisible_shape=activable_by_agent,
                         background=False,
                         texture=(0, 0, 0),
                         **entity_params)

        for texture in textures:

            if isinstance(texture, dict):
                texture = TextureGenerator.create(**texture)

            elif isinstance(texture, tuple):
                texture = ColorTexture(color=texture)

            assert isinstance(texture, Texture)
            texture.size = self._size_visible

            self.textures.append(texture)
            texture.generate()

        assert len(self.textures) > 1
        self.state = 0

        self._mode = mode
        self._texture_changed = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.texture = self.textures[self.state]
        self._texture_surface = self.texture.surface
        self._texture_changed = True

    def activate(self, activating: Union[Agent, Timer]):
        """
        When timer finishes, changes texture.

        Args:
            activating:
        """

        if self._mode == 'loop':
            self.state = (self.state + 1) % len(self.textures)

        elif self._mode == 'random':
            self.state = random.randint(0, len(self.textures) - 1)

        else:
            raise ValueError('not implemented')

        return None, None

    def draw(self, surface, draw_invisible=False, force_recompute_mask=False):

        super().draw(surface,
                     draw_invisible=draw_invisible,
                     force_recompute_mask=self._texture_changed)

        self._texture_changed = False

    def reset(self):

        super().reset()
        self.state = 0

    def _set_shape_collision(self):
        if self._activable_by_agent:
            assert self.pm_invisible_shape
            self.pm_invisible_shape.collision_type = CollisionTypes.ACTIVABLE

    @property
    def terminate_upon_activation(self):
        return False


class FlipReward(ColorChanging):
    """
    Changes the reward of an SceneElement based ColorChanging Element.
    """
    def __init__(
        self,
        element_changed: InteractiveElement,
        textures: List[Union[Texture, Dict, Tuple[int, int, int]]],
        mode: str = 'loop',
        activable_by_agent: bool = False,
        **kwargs,
    ):

        self.element_changed = element_changed
        super().__init__(textures=textures,
                         mode=mode,
                         activable_by_agent=activable_by_agent,
                         **kwargs)

        assert len(self.textures) == 2

        # pylint: disable=protected-access
        self._initial_reward = element_changed._reward

    def activate(self, _):

        super().activate(_)

        # pylint: disable=protected-access
        self.element_changed._reward = -self.element_changed._reward

        return None, None

    def reset(self):

        super().reset()

        # pylint: disable=protected-access
        self.element_changed._reward = self._initial_reward
