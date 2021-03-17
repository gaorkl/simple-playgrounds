# from simple_playgrounds.game_engine import Engine, RLibSingleAgentWrapper
# from simple_playgrounds.playground import PlaygroundRegister
# from simple_playgrounds.playgrounds.collection.rl.basic import EndgoalRoomCue
# from simple_playgrounds.agents.agents import BaseAgent
# from simple_playgrounds.agents.parts.platform import ForwardPlatform
# from simple_playgrounds.agents.sensors.robotic_sensors import RgbCamera, Touch
#
# from simple_playgrounds.agents.controllers import External
#
#
# def test_engine():
#
#     playground = EndgoalRoomCue()
#
#     agent = BaseAgent(controller=External(), interactive=False, platform=ForwardPlatform)
#     agent.add_sensor(RgbCamera(anchor=agent.base_platform))
#     agent.add_sensor(Touch(anchor=agent.base_platform))
#
#     env = RLibSingleAgentWrapper(agent, playground, time_limit=10000, multi_step=3)
#     obs = env.reset()
#
