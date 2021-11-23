import time

from simple_playgrounds.engine import Engine
from simple_playgrounds.agent.controllers import RandomContinuous
from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.playground.playgrounds.profiling_playgrounds import BasicUnmovable
from simple_playgrounds.device.sensors import SemanticCones, Touch, Position, Lidar

N_RUNS = 5
RUN_DURATION = 5000


def run_drones(pg_width, n_agents):

    n_elem_per_dim = int(pg_width / 100)
    size_elem = 20

    fps = 0

    for run in range(N_RUNS):

        pg = BasicUnmovable(size=(pg_width, pg_width), size_elements=size_elem, n_elements_per_dim=n_elem_per_dim)

        for agent in range(n_agents):

            my_agent = BaseAgent(controller=RandomContinuous(), lateral=False, rotate=True, interactive=False)

            sem_cones = SemanticCones(anchor=my_agent.base_platform,
                                  normalize=False,
                                  n_cones=36,
                                  rays_per_cone=4,
                                  max_range=200,
                                  fov=360)

            my_agent.add_sensor(sem_cones)

            lidar = Lidar(anchor= my_agent.base_platform,
                          normalize=False,
                          resolution=60,
                          max_range=300,
                          fov=180,
                          )

            my_agent.add_sensor(lidar)

            touch = Touch(anchor= my_agent.base_platform,
                          normalize=True,
                          fov=360,
                          max_range=5,
                          resolution=36)

            my_agent.add_sensor(touch)

            pos = Position(anchor=my_agent.base_platform)

            my_agent.add_sensor(pos)

            pg.add_agent(my_agent)

        engine_ = Engine(playground=pg, time_limit=RUN_DURATION)

        t_start = time.time()
        while engine_.game_on:

            actions = {}
            for agent in pg.agents:
                actions[agent] = agent.controller.generate_actions()

            engine_.step(actions=actions)
            engine_.update_observations()

        t_end = time.time()

        fps += (RUN_DURATION/ (t_end - t_start)) / N_RUNS

    return fps


if __name__ == '__main__':

    for n_agents in [1, 2, 5, 10, 20]:

        for pg_width in [400, 600, 1000]:

            res = run_drones(pg_width, n_agents)

            print(n_agents, pg_width, res)