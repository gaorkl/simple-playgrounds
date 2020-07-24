
from simple_playgrounds.entities.agents.sensors import *

from simple_playgrounds.controllers import Random
from simple_playgrounds.entities.agents import BaseAgent, BaseInteractiveAgent,\
                                                TurretAgent, ArmHandAgent, HeadEyeAgent,ArmAgent
from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *


# Run all test playgrounds with basic non-interactive agent
def test_base_agent_on_all_test_playgrounds():

    print('Testing of BaseAgent..............')

    agent = BaseAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")



def test_baseinteractive_agent_on_all_test_playgrounds():

    print('Testing of BaseInteractiveAgent..............')

    agent = BaseInteractiveAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent_without_overlapping(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")


def test_turret_agent_on_all_test_playgrounds():

    print('Testing of TurretAgent..............')

    agent = TurretAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent_without_overlapping(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")


def test_armhand_agent_on_all_test_playgrounds():

    print('Testing of ArmHandAgent..............')

    agent = ArmHandAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent_without_overlapping(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")


def test_headeye_agent_on_all_test_playgrounds():

    print('Testing of HeadEyeAgent..............')

    agent = HeadEyeAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent_without_overlapping(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")


def test_arm_agent_on_all_test_playgrounds():

    print('Testing of ArmAgent..............')

    agent = ArmAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        success = pg.add_agent_without_overlapping(agent, tries=100)

        if success:
            print('Starting testing of ', pg_class.__name__)

            engine = Engine(pg, time_limit=1000, replay=False)
            engine.run()

            assert 0 < agent.position[0] < pg.size[0]
            assert 0 < agent.position[1] < pg.size[1]

            pg.remove_agent(agent)

        else:
            print("Couldn't place agent")

