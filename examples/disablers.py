from spg.agent import HeadAgent
from spg.agent.sensor import RGBSensor
from spg.element import Ball, SensorDisabler
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

gui = GUI(playground, agent)
gui.run()

playground.debug_draw()
