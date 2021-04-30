from simple_playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds import scene_elements
from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.utils.position_utils import (CoordinateSampler,
                                                     Trajectory)


@PlaygroundRegister.register('foraging', 'candy_poison')
class CandyPoisonEnv(SingleRoom):
    def __init__(self):
        super().__init__(size=(200, 200))

        # Starting area of the agent
        area_center, _ = self.area_rooms[(0, 0)]
        area_start = CoordinateSampler(center=area_center,
                                       area_shape='rectangle',
                                       width_length=(100, 100))
        self.agent_starting_area = area_start

        additional_types = set()
        for loc in ["down-left", "up-right"]:
            area_center, size_area = self.get_area((0, 0), loc)
            area = CoordinateSampler(center=area_center,
                                     area_shape='rectangle',
                                     width_length=size_area)
            field = scene_elements.Field(entity_produced=scene_elements.Candy,
                                         production_area=area,
                                         probability=0.01,
                                         limit=2)
            self.add_scene_element(field)
            additional_types.add(field.entity_produced)

            field = scene_elements.Field(entity_produced=scene_elements.Poison,
                                         production_area=area,
                                         probability=0.01,
                                         limit=2)
            self.add_scene_element(field)
            additional_types.add(field.entity_produced)

        self.time_limit = 2000
        self.time_limit_reached_reward = -1

        self.create_entity_types_map(additional_types)


@PlaygroundRegister.register('foraging', 'candy_fireballs')
class CandyFireballs(SingleRoom):
    def __init__(self, time_limit=100, probability_production=0.4):

        super().__init__(size=(200, 200))

        fireball_texture = {
            'texture_type': 'centered_random_tiles',
            'size_tiles': 4
        }

        additional_types = set()

        # First Fireball
        text_1 = {'color_min': [220, 0, 200], 'color_max': [255, 100, 220]}
        trajectory = Trajectory('waypoints',
                                trajectory_duration=300,
                                waypoints=[[20, 20], [20, 180], [180, 180],
                                           [180, 20]])
        fireball = scene_elements.Fireball(texture={
            **fireball_texture,
            **text_1
        })
        self.add_scene_element(fireball, trajectory)
        additional_types.add(type(fireball))

        # Second Fireball
        text_2 = {'color_min': [180, 0, 0], 'color_max': [220, 100, 0]}
        trajectory = Trajectory('waypoints',
                                trajectory_duration=150,
                                waypoints=[[40, 40], [160, 160]])
        fireball = scene_elements.Fireball(texture={
            **fireball_texture,
            **text_2
        })
        self.add_scene_element(fireball, trajectory)

        # Third Fireball
        text_3 = {'color_min': [220, 100, 0], 'color_max': [255, 120, 0]}
        trajectory = Trajectory('waypoints',
                                trajectory_duration=180,
                                waypoints=[[40, 160], [160, 40]])
        fireball = scene_elements.Fireball(texture={
            **fireball_texture,
            **text_3
        })
        self.add_scene_element(fireball, trajectory)

        # Foraging
        area_prod = CoordinateSampler(center=(100, 100),
                                      area_shape='rectangle',
                                      width_length=(150, 150))

        field = scene_elements.Field(scene_elements.Candy,
                                     production_area=area_prod,
                                     probability=probability_production)
        self.add_scene_element(field)
        additional_types.add(field.entity_produced)

        self.time_limit = time_limit

        self.create_entity_types_map(additional_types)
