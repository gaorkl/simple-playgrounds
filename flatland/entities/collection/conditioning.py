from ..entity import Entity

class ColorChanging(Entity):

    entity_type = 'color_changing'
    timed = True

    def __init__(self, initial_position, timers, textures, **kwargs):
        """ Base class for traffic light entities

        Traffic Light entity changes color and is controlled at the level of the playground.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: can be 'apple' or 'rotten_apple'
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            shrink_ratio_when_eaten: When eaten by an agent, the mass, size, and reward are multiplied by this ratio.
                Default: 0.9
            initial_reward: Initial reward of the edible
            min_reward: When reward is lower than min_reward, the edible entity disappears

        """

        default_config = self._parse_configuration('basic', 'color_changing')
        entity_params = {**default_config, **kwargs}

        if isinstance(timers, int):
            self.timers = [timers]
        else:
            assert isinstance(timers, (list, tuple))
            self.timers = timers

        if isinstance(textures, (list, tuple)):
            self.list_texture_params = textures
        else:
            self.list_texture_params = [textures]

        assert len(self.list_texture_params) == len(self.timers)

        super().__init__(initial_position=initial_position, **entity_params)


        self.textures = []
        for texture in self.list_texture_params:
            texture_surface = self.create_texture(texture)
            self.textures.append(texture_surface)

        self.texture_surface = self.textures[0]
        self.force_redraw = False
        self.reset_timer()


    def reset_timer(self):

        self.current_index = 0
        self.timer = self.timers[self.current_index]
        self.force_redraw = True

    def update(self):

        self.timer -= 1

    def activate(self, activating_entity):

        self.current_index = (self.current_index + 1) % len(self.timers)

        self.timer = self.timers[self.current_index]
        self.texture_surface = self.textures[self.current_index]

        self.force_redraw = True

        return [], []

    def draw(self, surface, draw_interaction=False, force_recompute_mask=False):

        super().draw(surface, draw_interaction=draw_interaction, force_recompute_mask=self.force_redraw)
        self.force_redraw = False


    def reset(self):

        super().reset()
        self.reset_timer()


class ConditionedColorChanging(ColorChanging):

    def __init__(self, initial_position, conditioned_entity, timers, textures, **kwargs):

        super().__init__(initial_position, timers, textures, **kwargs)

        self.conditioned_entity = conditioned_entity

    def activate(self, activating_entity):

        super().activate(activating_entity)

        self.conditioned_entity.reward = -self.conditioned_entity.reward

        return [], []