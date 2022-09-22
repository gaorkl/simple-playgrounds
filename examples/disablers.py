from spg.agent import HeadAgent
from spg.agent.controller import GrasperController
from spg.agent.sensor import RGBSensor
from spg.element import Ball, ControllerDisabler, SensorDisabler
from spg.playground import WallClosedPG
from spg.view import GUI

playground = WallClosedPG(size=(400, 400))

ball = Ball()
ball.graspable = True

playground.add(ball, ((150, 150), 0))

agent = HeadAgent()
playground.add(agent)

sensor_disabler = SensorDisabler(sensors=RGBSensor)
playground.add(sensor_disabler, ((150, -150), 0))

sensor_disabler = SensorDisabler()
playground.add(sensor_disabler, ((150, 0), 0))

controller_disabler = ControllerDisabler(controllers=GrasperController)
playground.add(controller_disabler, ((-150, -150), 0))

controller_disabler = ControllerDisabler()
playground.add(controller_disabler, ((-150, 0), 0))

gui = GUI(playground, agent)
gui.run()
