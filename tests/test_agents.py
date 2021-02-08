
from simple_playgrounds.agents.sensors import *

from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents.agents import BaseAgent, BaseInteractiveAgent,\
                                                TurretAgent, ArmHandAgent, HeadEyeAgent,ArmAgent
from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *
from simple_playgrounds.playgrounds import SingleRoom


# Run all test playgrounds with basic non-interactive agent
def test_base_agent_on_all_test_playgrounds():

    print('Testing of BaseAgent..............')

    agent = BaseAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=1000)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)


def test_baseinteractive_agent_on_all_test_playgrounds():

    print('Testing of BaseInteractiveAgent..............')

    agent = BaseInteractiveAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=1000)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)


def test_turret_agent_on_all_test_playgrounds():

    print('Testing of TurretAgent..............')

    agent = TurretAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=1000)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)


def test_agents_in_empty_playgrounds():

    pg = SingleRoom()
    center, shape = pg.area_rooms[(0, 0)]
    pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)


    agent = ArmHandAgent(controller=Random(), allow_overlapping=False)
    print('Starting testing of ', ArmHandAgent.__name__)

    agent.initial_position = pos_area_sampler
    pg.add_agent(agent)

    engine = Engine(pg, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < pg.size[0]
    assert 0 < agent.position[1] < pg.size[1]

    pg.remove_agent(agent)

    agent = HeadEyeAgent(controller=Random(), allow_overlapping=False)
    print('Starting testing of ', HeadEyeAgent.__name__)

    agent.initial_position = pos_area_sampler
    pg.add_agent(agent)

    engine = Engine(pg, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < pg.size[0]
    assert 0 < agent.position[1] < pg.size[1]

    pg.remove_agent(agent)

    agent = ArmAgent(controller=Random(), allow_overlapping=False)
    print('Starting testing of ', ArmAgent.__name__)

    agent.initial_position = pos_area_sampler
    pg.add_agent(agent)

    engine = Engine(pg, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < pg.size[0]
    assert 0 < agent.position[1] < pg.size[1]

    pg.remove_agent(agent)



def test_headeye_agent_on_all_test_playgrounds():

    print('Testing of HeadEyeAgent..............')

    agent = HeadEyeAgent(controller=Random())

    for pg_class in PlaygroundRegister.filter('test'):

        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=1000)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)



def test_arm_agent_on_all_test_playgrounds():

    print('Testing of ArmAgent..............')

    agent = ArmAgent(controller=Random(), allow_overlapping=False)

    for pg_class in PlaygroundRegister.filter('test'):


        pg = pg_class()

        center, shape = pg.area_rooms[(0, 0)]
        pos_area_sampler = PositionAreaSampler(center=center, area_shape='rectangle', width_length=shape)
        agent.initial_position = pos_area_sampler

        pg.add_agent(agent, tries=1000)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=1000)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)


