
from simple_playgrounds.playgrounds import SingleRoom, LinearRooms, ConnectedRooms2D

from simple_playgrounds.controllers import Random
from simple_playgrounds.entities.agents import BaseAgent, BaseInteractiveAgent
from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *
from simple_playgrounds.playgrounds.collection.test.test_scene_elements import Doors

# Add/remove agent from a playground
def test_add_remove_agent():
    playground_1 = SingleRoom(size=(200, 200))
    playground_2 = SingleRoom(size=(200, 200))
    agent = BaseAgent(controller=Random())
    playground_1.add_agent(agent)
    playground_1.remove_agent(agent)
    assert playground_1.agents == []
    playground_2.add_agent(agent)

# Create an engine then add an agent
def test_engine():
    playground = SingleRoom(size=(200, 200))
    agent = BaseAgent(controller=Random())
    engine = Engine(playground, time_limit=100)
    playground.add_agent(agent)
    assert len(engine.agents) == 1
    playground.remove_agent(agent)
    assert len(engine.agents) == 0


# Run the playground, check that position changed
def test_engine_run():
    playground = SingleRoom(size=(200, 200))
    agent = BaseAgent(controller=Random())
    engine = Engine(playground, agents=agent, time_limit=100)

    pos_start = agent.position
    assert pos_start == (100., 100., 0.)
    engine.run()
    assert pos_start != agent.position

    playground.remove_agent(agent)
    engine = Engine(playground, agents=agent, time_limit=100)
    engine.run()

    playground.remove_agent(agent)
    engine = Engine(playground,  time_limit=100)
    playground.add_agent(agent)
    engine.run()



# Run all test playgrounds with basic non-interactive agent
def test_all_test_playgrounds():

    agent = BaseAgent(controller=Random())

    for pg_class in PlaygroundRegister.subclasses['test']:
        pg = pg_class()

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=10000, replay=False)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)
        pg.reset()


# Run all test playgrounds with basic non-interactive agent
def test_grasp_playgrounds():

    for pg_class in PlaygroundRegister.subclasses['test-grasp']:

        pg = pg_class()
        print('Starting testing of ', pg_class.__name__)

        agent = BaseInteractiveAgent(controller=Random())

        engine = Engine(pg, agents=agent, time_limit=10000, replay=False)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)
        pg.reset()

# Run all test playgrounds with 10 agents
def test_multiagents():

    for pg_class in PlaygroundRegister.subclasses['test']:

        pg = pg_class()
        print('Starting Multiagent testing of ', pg_class.__name__)
        center, shape = pg.area_rooms[(0,0)]
        pos_area_sampler = PositionAreaSampler(center = center, area_shape='rectangle', width_length=shape)

        for i in range(20):
            agent = BaseInteractiveAgent(pos_area_sampler, controller=Random())
            pg.add_agent_without_overlapping(agent, 1000)

        assert len(pg.agents) == 20

        engine = Engine(pg, time_limit=10000, replay=False, screen=False)
        engine.run(with_screen = False)

            # pg.remove_agent(agent)
            # pg.reset()