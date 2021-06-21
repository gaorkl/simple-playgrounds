"""
Scene Elements used for conditioning experiments
"""
from typing import List, Union, Dict, Tuple

import random

from ..element import InteractiveElement
from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from ...configs.parser import parse_configuration
from ...common.texture import Texture, TextureGenerator, ColorTexture


class ColorChanging(InteractiveElement):
    """ SceneElement that changes its texture when activated."""

    def __init__(self,
                 textures: List[Union[Texture, Dict, Tuple[int, int, int]]],
                 mode: str = 'loop',
                 activable_by_agent: bool = False,
                 **kwargs,
                 ):

        entity_params = parse_configuration('element_conditioning', config_key=ElementTypes.COLOR_CHANGING)
        entity_params = {**kwargs, **entity_params}

        self.textures = []
        self._activable_by_agent = activable_by_agent

        super().__init__(visible_shape=True, invisible_shape=activable_by_agent, background=False,texture=(0, 0, 0), **entity_params)

        for texture in textures:

            if isinstance(texture, Dict):
                texture['size'] = self._size_visible
                texture = TextureGenerator.create(**texture)

            elif isinstance(texture, tuple):
                texture = ColorTexture(size=self._size_visible, color=texture)

            assert isinstance(texture, Texture)

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

    def activate(self, _):
        """
        When timer finishes, changes texture.

        Args:
            activating_entity: must be Playground.
        """

        if self._mode == 'loop':
            self.state = (self.state + 1) % len(self.textures)

        elif self._mode == 'random':
            self.state = random.randint(0, len(self.textures) - 1)

        else:
            raise ValueError('not implemented')

        return None, None

    def draw(self,
             surface,
             draw_invisible=False,
             force_recompute_mask=False):

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


class RewardFlipper(ColorChanging):
    """
    Flips the reward of an SceneElement based ColorChanging Element
    """
    def __init__(self,
                 element_flipped: InteractiveElement,
                 textures: List[Union[Texture, Dict, Tuple[int, int, int]]],
                 mode: str = 'loop',
                 activable_by_agent: bool = False,
                 **kwargs,
                 ):

        self.element_flipped = element_flipped
        super().__init__(textures=textures, mode=mode, activable_by_agent=activable_by_agent, **kwargs)
        assert len(self.textures) == 2

    def activate(self, _):

        super().activate(None)

        if self.state == 0:
            self.element_flipped.reward = abs(self.element_flipped.reward)
        else:
            self.element_flipped.reward = -abs(self.element_flipped.reward)

        return None, None
