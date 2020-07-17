from flatland.playgrounds import SingleRoom, LinearRooms, ConnectedRooms2D
from flatland.entities.agents import BaseAgent

agent = BaseAgent()

# Add agent to a playground
playground = SingleRoom(size=(200, 200))
playground.add_agent(agent)

#
# initial_position = PositionAreaSampler(area_shape='circle', center=[100 , 100], radius=100)
# # initial_position = [25,25, math.pi/4]
# my_agent = BaseAgent(name = 'test_agent', initial_position=initial_position, controller=Random())
#
#
# from flatland.game_engine import Engine
#
#
# game = Engine(playground=pg, agents=agents, time_limit=1000, replay=True, screen=True)
