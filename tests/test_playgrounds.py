from simple_playgrounds.playgrounds import SingleRoom, LinearRooms, ConnectedRooms2D
from simple_playgrounds.controllers import Random
from simple_playgrounds.entities.agents import BaseAgent
from simple_playgrounds.game_engine import Engine

agent = BaseAgent(controller=Random())

# Add/remove agent from a playground
playground = SingleRoom(size=(200, 200))
playground.add_agent(agent)
playground.remove_agent(agent)
assert playground.agents == []

# Create an engine then add an agent
engine = Engine(playground, time_limit=100)
playground.add_agent(agent)
assert len(engine.agents) == 1

# Run the playground, check that position changed
pos_start = agent.position
assert pos_start == (100., 100., 0.)
engine.run()
assert pos_start != agent.position

