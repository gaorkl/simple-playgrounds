from simple_playgrounds.playgrounds.collection import *

from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.parts.controllers import Keyboard
from simple_playgrounds.agents.agents import BaseAgent
import simple_playgrounds.agents.sensors as sensors

import cv2

my_agent = BaseAgent(controller=Keyboard(), lateral=True, interactive=True)

# ----------------------------------------------------------
rgb = sensors.RgbCamera(my_agent.base_platform,
                invisible_elements=my_agent.parts,
                fov=180,
                resolution=64,
                max_range=500,
                normalize = True)
my_agent.add_sensor(rgb)

rgb = sensors.RgbCamera(my_agent.base_platform,
                fov=180,
                resolution=64,
                max_range=500,
                normalize=False)
my_agent.add_sensor(rgb)

# grey = sensors.GreyCamera(my_agent.head, invisible_elements=my_agent.parts, fov=180, resolution=64, max_range=500)
# my_agent.add_sensor(grey)

lidar = sensors.Lidar(my_agent.base_platform, normalize=False, invisible_elements=my_agent.parts, fov=180, resolution=128, max_range=400)
my_agent.add_sensor(lidar)

# depth = sensors.Proximity(my_agent.base_platform, normalize=False, invisible_elements=my_agent.parts, fov=100, resolution=64, max_range=400)
# my_agent.add_sensor(depth)

touch = sensors.Touch(my_agent.base_platform, normalize=True, invisible_elements=my_agent.parts)
my_agent.add_sensor(touch)

sem_ray = sensors.SemanticRay(my_agent.base_platform, invisible_elements=my_agent.parts, remove_duplicates=False, fov=90)
my_agent.add_sensor(sem_ray)

sem_cones = sensors.SemanticCones(my_agent.base_platform, invisible_elements=my_agent.parts, normalize=True, remove_duplicates=False)
my_agent.add_sensor(sem_cones)

td = sensors.TopdownLocal(my_agent.base_platform, invisible_elements=my_agent.parts, normalize=True, only_front=True, fov=180)
my_agent.add_sensor(td)

fi = sensors.TopDownGlobal(my_agent.base_platform, resolution=64, normalize=False)
my_agent.add_sensor(fi)

fi = sensors.PerfectSemantic(my_agent.base_platform)
my_agent.add_sensor(fi)


fi = sensors.PerfectSemantic(my_agent.base_platform, fov=180)
my_agent.add_sensor(fi)

fi = sensors.Position(my_agent.base_platform)
my_agent.add_sensor(fi)

fi = sensors.Velocity(my_agent.base_platform)
my_agent.add_sensor(fi)

fi = sensors.RelativeVelocity(my_agent.base_platform)
my_agent.add_sensor(fi)


###### Test noise Sensors
#
# noise_gaussian = {'type': 'gaussian', 'mean': 0, 'scale': 5}
# noise_sp = {'type': 'salt_pepper', 'probability': 0.05}
#
# # ----------------------------------------------------------
# rgb = RgbCamera(my_agent.head, invisible_elements=my_agent.parts, resolution=64, max_range=600, noise_params=noise_gaussian)
# my_agent.add_sensor(rgb)
# #
# grey = GreyCamera(my_agent.head, invisible_elements=my_agent.parts, fov=180, resolution=64, max_range=100, noise_params=noise_gaussian)
# my_agent.add_sensor(grey)
#
# # ----------------------------------------------------------
# lidar = Lidar(my_agent.head, normalize=False, invisible_elements=my_agent.parts, fov=100, resolution=64, max_range=200, noise_params=noise_sp)
# my_agent.add_sensor(lidar)
#
# noise_gaussian_touch = {'type': 'gaussian', 'mean': 0, 'scale': 1}
# touch = Touch(my_agent.base_platform, normalize=True, invisible_elements=my_agent.parts, noise_params=noise_gaussian_touch)
# my_agent.add_sensor(touch)
#
# # ----------------------------------------------------------
# td = TopdownSensor(my_agent.head, invisible_elements=my_agent.parts, normalize=True, only_front=True, noise_params=noise_sp)
# my_agent.add_sensor(td)

#################################

for playground_name, pg_class in PlaygroundRegister.playgrounds['demo'].items():

    pg = pg_class()
    pg.add_agent(my_agent, allow_overlapping=False)

    engine = Engine(playground=pg, screen=True, debug=False)

    while engine.game_on:

        engine.update_screen()

        actions = {}
        for agent in engine.agents:
            actions[agent] = agent.controller.generate_actions()

        engine.multiple_steps(actions=actions, n_steps=2)
        engine.update_observations(grasped_invisible=True)

        cv2.imshow(
            'agent',
            engine.generate_agent_image(my_agent,
                                        layout=(('sensors', 'playground'),
                                                'actions')))

        cv2.waitKey(1)

    pg.remove_agent(my_agent)

