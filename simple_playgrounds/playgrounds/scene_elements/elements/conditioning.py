"""
Scene Elements used for conditioning experiments
"""
from simple_playgrounds.playground import Playground
from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.playgrounds.scene_elements.elements.interactive import Lever
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import SceneElementTypes


class ColorChanging(SceneElement):

    """ SceneElement that changes its texture based on a timer."""

    entity_type = SceneElementTypes.COLOR_CHANGING
    timed = True

    def __init__(self, timers, textures, **kwargs):
        """

        ColorChanging changes color and is controlled at the level of the playground.
        The color changes depending on a list of timers.

        Args:
            timers: Single timer (int) or list of Timers.
            textures: Single texture or list of Textures.
            **kwargs: other params to configure entity. Refer to Entity class.
        """

        default_config = parse_configuration('element_basic', self.entity_type)
        entity_params = {**default_config, **kwargs}

        if isinstance(timers, int):
            self.timers = [timers]
        else:
            if not isinstance(timers, (list, tuple)):
                raise ValueError("timers should be int, list or tuple")
            self.timers = timers

        if isinstance(textures, (list, tuple)):
            self.list_texture_params = textures
        else:
            self.list_texture_params = [textures]

        assert len(self.list_texture_params) == len(self.timers)

        super().__init__(**entity_params)

        self.textures = []
        for texture in self.list_texture_params:
            texture_surface = self._create_texture(texture)
            self.textures.append(texture_surface)

        self.texture_surface = self.textures[0]
        self.force_redraw = False

        self.timer = 0
        self.current_index = 0
        self._reset_timer()

    def _reset_timer(self):

        self.current_index = 0
        self.timer = self.timers[self.current_index]
        self.force_redraw = True

    def pre_step(self):

        self.timer -= 1

    def activate(self, activating_entity):
        """
        When timer finishes, changes texture.

        Args:
            activating_entity: must be Playground.
        """

        assert isinstance(activating_entity, Playground)

        self.current_index = (self.current_index + 1) % len(self.timers)

        self.timer = self.timers[self.current_index]
        self.texture_surface = self.textures[self.current_index]
        self.force_redraw = True

        return [], []

    def draw(self, surface, draw_interaction=False, force_recompute_mask=False):

        super().draw(surface, draw_interaction=draw_interaction,
                     force_recompute_mask=self.force_redraw)
        self.force_redraw = False

    def reset(self):

        super().reset()
        self._reset_timer()


class ConditionedColorChanging(ColorChanging):
    """
    Flips the reward of an SceneElement based on timers.
    Intended to work with Lever SceneElement.
    """

    def __init__(self, conditioned_entity, timers, textures, **kwargs):
        """

        Args:
            conditioned_entity: Lever SceneElement.
            timers: list of Timers.
            textures: list of Textures.
            **kwargs: other params to configure entity. Refer to Entity class.

        Notes:
            The length of timers and textures should be 2.
        """

        if not isinstance(conditioned_entity, Lever):
            raise ValueError('conditioned_entity must be of class Lever')

        assert len(timers) == len(textures) == 2

        super().__init__(timers, textures, **kwargs)

        self.conditioned_entity = conditioned_entity

    def activate(self, activating_entity):
        """
        When timers finishes, change color and flip rewards.
        """

        super().activate(activating_entity)

        self.conditioned_entity.reward = -self.conditioned_entity.reward

        return [], []
