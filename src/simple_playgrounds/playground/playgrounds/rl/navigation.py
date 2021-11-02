import random
from typing import Optional

from simple_playgrounds.playground.layouts import GridRooms, SingleRoom
from simple_playgrounds.playground.playground import PlaygroundRegister
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.element.elements.basic import Physical
from simple_playgrounds.element.elements.zone import DeathZone, GoalZone


@PlaygroundRegister.register('basic_rl', 'endgoal_cue')
class EndgoalRoomCue(SingleRoom):
    """
    Squared environment with obstacles.
    The agent must reach the correct corner, indicated by the color of
    a center object.
    """
    def __init__(
        self,
        time_limit=1000,
        reward_reached_time_limit=-10,
        reward_reached_endgoal=10,
        reward_reached_deathtrap=-10,
        playground_seed: Optional[int] = None,
    ):

        super().__init__(size=(200, 200), playground_seed=playground_seed)

        # Starting area of the agent
        area_center = self.grid_rooms[0][0].center
        area_start = CoordinateSampler(center=area_center,
                                       area_shape='rectangle',
                                       size=(100, 100))
        self.initial_agent_coordinates = area_start

        # Visual Cues for the agent to orient itself.
        obstacle_1 = Physical(config_key='pentagon', radius=9)
        self.add_element(obstacle_1, ((60, 30), 0.34))

        obstacle_2 = Physical(config_key='rectangle', size=[8, 12])
        self.add_element(obstacle_2, ((130, 150), 1.7))

        obstacle_3 = Physical(config_key='square', radius=8)
        self.add_element(obstacle_3, ((40, 140), 0.4))

        obstacle_4 = Physical(physical_shape='triangle',
                              radius=14,
                              texture=(150, 200, 200))
        self.add_element(obstacle_4, ((160, 60), 0))

        self.goal = None
        self.cue = None

        self.goal_locations = (((20, 20), 0), ((180, 20), 0), ((180, 180), 0),
                               ((20, 180), 0))
        self.cue_colors = ((200, 50, 200), (50, 200, 50), (200, 50, 50),
                           (50, 50, 200))

        self.reward_goal = reward_reached_endgoal
        self.reward_deathtrap = reward_reached_deathtrap

        self._set_goal()

        self.time_limit = time_limit
        self.time_limit_reached_reward = reward_reached_time_limit

    def _set_goal(self):

        index_goal = random.randint(0, 3)
        loc = self.goal_locations[index_goal]
        col = self.cue_colors[index_goal]

        if self.goal is not None:
            self._remove_element_from_playground(self.goal)
            self._remove_element_from_playground(self.cue)

        self.cue = Physical(physical_shape='circle',
                            radius=10,
                            texture=col,
                            is_temporary_entity=True)
        self.add_element(self.cue, ((100, 100), 0))

        self.goal = GoalZone(reward=self.reward_goal, is_temporary_entity=True)
        self.add_element(self.goal, loc)

        for i in range(4):
            if i != index_goal:
                loc = self.goal_locations[i]
                other_goal = DeathZone(reward=self.reward_deathtrap,
                                       is_temporary_entity=True)
                self.add_element(other_goal, loc)

    def reset(self):
        super().reset()
        self._set_goal()


@PlaygroundRegister.register('navigation', 'endgoal_9rooms')
class Endgoal9Rooms(GridRooms):
    """
    Squared environment composed of 9 rooms (3x3).
    The agent must reach the invisible goal in the left-down corner.
    Each wall has a different color.
    """
    def __init__(
        self,
        time_limit=1000,
        playground_seed: Optional[int] = None,
    ):

        super().__init__(size=(450, 450),
                         room_layout=(3, 3),
                         wall_type='colorful',
                         playground_seed=playground_seed,
                         doorstep_size=60)

        # Starting area of the agent
        area_start = CoordinateSampler(center=(225, 225),
                                       area_shape='rectangle',
                                       size=(450, 450))
        self.initial_agent_coordinates = area_start

        # invisible endzone at one corner of the game
        invisible_endzone = GoalZone(reward=10)
        self.add_element(invisible_endzone, ((20, 20), 0))

        self.time_limit = time_limit
