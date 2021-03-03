
from simple_playgrounds.agents.sensors import *

from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents.parts.platform import ForwardPlatform, FixedPlatform, HolonomicPlatform, ForwardBackwardPlatform
from simple_playgrounds.agents.agents import BaseAgent, HeadAgent, HeadEyeAgent, TurretAgent, FullAgent
from simple_playgrounds.playgrounds.empty import SingleRoom, LinearRooms, ConnectedRooms2D

from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *
from simple_playgrounds.playgrounds import SingleRoom


def run_engine(agent, pg_class):

    pg = pg_class()

    pg.add_agent(agent)

    print('Starting testing of ', pg_class.__name__)

    engine = Engine(pg, time_limit=1000)
    engine.run()

    assert 0 < agent.position[0] < pg.size[0]
    assert 0 < agent.position[1] < pg.size[1]

    pg.remove_agent(agent)


# Run all test playgrounds with BaseAgent
def test_base_agent():

    print('Testing of BaseAgent...')

    for interactive in [True, False]:

        if interactive:
            print('.... with interactions')
        else:
            print('.... without interactions')

        for platform in ForwardPlatform, FixedPlatform, HolonomicPlatform, ForwardBackwardPlatform:

            print('......... on platform'+ str(platform) )

            agent = BaseAgent(controller=Random(), interactive=interactive, platform=platform)

            for pg_class in PlaygroundRegister.filter('test'):
                run_engine(agent, pg_class)


def test_headagent():

    print('Testing of HeadAgent..............')

    for interactive in [True, False]:

        if interactive:
            print('.... with interactions')
        else:
            print('.... without interactions')

        for platform in ForwardPlatform, FixedPlatform, HolonomicPlatform, ForwardBackwardPlatform:

            print('......... on platform' + str(platform))

            agent = HeadAgent(controller=Random(), interactive=interactive, platform=platform)

            for pg_class in PlaygroundRegister.filter('test'):
                run_engine(agent, pg_class)


def test_headeyeagent():

    print('Testing of HeadEyeAgent..............')

    for interactive in [True, False]:

        if interactive:
            print('.... with interactions')
        else:
            print('.... without interactions')

        for platform in ForwardPlatform, FixedPlatform, HolonomicPlatform, ForwardBackwardPlatform:

            print('......... on platform' + str(platform))

            agent = HeadEyeAgent(controller=Random(), interactive=interactive, platform=platform)

            for pg_class in PlaygroundRegister.filter('test'):
                run_engine(agent, pg_class)


def test_turretagent():

    print('Testing of TurretAgent..............')

    for interactive in [True, False]:

        if interactive:
            print('.... with interactions')
        else:
            print('.... without interactions')

        agent = TurretAgent(controller=Random(), interactive=interactive)

        for pg_class in PlaygroundRegister.filter('test'):
            run_engine(agent, pg_class)


def test_agent_initial_position():

    print('Testing of intital position agent')

    agent = BaseAgent(controller=Random(), interactive=False, platform=ForwardPlatform)

    # Default Case
    pg = SingleRoom( (300, 300) )
    pg.add_agent(agent)

    assert 0 < agent.position[0] < pg.size[0]
    assert 0 < agent.position[1] < pg.size[1]

    pg.remove_agent(agent)

    pg = ConnectedRooms2D((400, 400), (2, 2))
    pg.add_agent(agent)

    assert 0 < agent.position[0] < 200
    assert 0 < agent.position[1] < 200

    pg.remove_agent(agent)

    # Modifying initial position in playground
    pg = SingleRoom((300, 300))
    pg.initial_agent_position = (50, 50, 0)
    pg.add_agent(agent)
    assert (agent.position == (50, 50, 0))
    pg.remove_agent(agent)

    # Setting initial position in playground as PositionAreaSampler
    pg = SingleRoom((300, 300))
    center, shape = pg.area_rooms[(0, 0)]
    pg.initial_agent_position = PositionAreaSampler(center, area_shape='rectangle', width_length=shape)
    pg.add_agent(agent)
    pos_1 = agent.position
    pg.remove_agent(agent)
    pg.add_agent(agent)
    assert (agent.position != pos_1)
    pg.remove_agent(agent)
