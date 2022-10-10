from spg.agent import HeadAgent
from spg.agent.controller import GrasperController
from spg.agent.sensor import RGBSensor
from spg.element import Ball, CommunicatorDisabler, ControllerDisabler, SensorDisabler
from spg.playground import Room
from spg.view import HeadAgentGUI

playground = Room(size=(400, 400))

ball = Ball()
ball.graspable = True

playground.add(ball, ((0, 150), 0))

agent = HeadAgent()
playground.add(agent)

agent_2 = HeadAgent()
playground.add(agent_2, ((0, 150), 0))

sensor_disabler = SensorDisabler(sensors=RGBSensor)
playground.add(sensor_disabler, ((150, -150), 0))

sensor_disabler = SensorDisabler()
playground.add(sensor_disabler, ((150, 0), 0))

controller_disabler = ControllerDisabler(controllers=GrasperController)
playground.add(controller_disabler, ((-150, -150), 0))

controller_disabler = ControllerDisabler()
playground.add(controller_disabler, ((-150, 0), 0))

communicator_disabler = CommunicatorDisabler()
playground.add(communicator_disabler, ((150, 150), 0))

communicator_disabler = CommunicatorDisabler()
playground.add(communicator_disabler, ((-150, 150), 0))


gui = HeadAgentGUI(playground, agent, random_agents=True)
gui.run()
