# from simple_playgrounds.playgrounds.collection.rl.navigation import EndgoalRoomCue, Endgoal9Rooms
# from simple_playgrounds.playgrounds.collection.rl.foraging import CandyFireballs
# from simple_playgrounds.playgrounds.collection.rl.sequential import DispenserEnv, DoorDispenserCoin

from simple_playgrounds.playgrounds.collection.test.test_playgrounds import *
from simple_playgrounds.playgrounds.playground import PlaygroundRegister

# from simple_playgrounds.playgrounds import SingleRoom, GridRooms

from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.parts.controllers import Keyboard, RandomContinuous, RandomDiscrete
from simple_playgrounds.agents.agents import HeadAgent
from simple_playgrounds.agents.sensors import *
import cv2
import time

# my_playground = SingleRoom(size=(100, 400), playground_seed=12)
# my_playground = GridRooms(size=(300, 400), room_layout=(2, 3), doorstep_size=50, wall_depth=5)#, playground_seed=12)

print(PlaygroundRegister.playgrounds)
my_playground = Teleports()

# d = my_playground.grid_rooms[0][0].doorstep_right.generate_door()
# my_playground.add_element(d)

my_agent = HeadAgent(controller=Keyboard(), lateral=True, interactive=True)
# dummy = HeadAgent(controller=Random(), platform=ForwardBackwardPlatform, interactive=True)
# Noisy agent
# noise_motor = {'type': 'gaussian', 'mean': 0, 'scale': 0.01}
# my_agent = HeadAgent(controller=Keyboard(), noise_params=noise_motor)

# circul = Basic( default_config_key='circle', movable = True, mass = 5, graspable = True)
# my_playground.add_scene_element(circul, ((100, 50), 0))
# rgb = RgbCamera(circul, invisible_elements=my_agent.parts, resolution=64, max_range=600)
# my_agent.add_sensor(rgb)

# ----------------------------------------------------------
rgb = RgbCamera(my_agent.base_platform,
                invisible_elements=my_agent.parts,
                fov=180,
                resolution=64,
                max_range=500)
my_agent.add_sensor(rgb)

# rgb = RgbCamera(my_agent.base_platform, fov=180, resolution=64, max_range=500)
# my_agent.add_sensor(rgb)

# rgb = RgbCamera(my_agent.base_platform, min_range=my_agent.base_platform.radius, fov=180, resolution=64, max_range=500)
# my_agent.add_sensor(rgb)

# grey = GreyCamera(my_agent.base_platform, invisible_elements=my_agent.parts, fov=180, resolution=64, max_range=500)
# my_agent.add_sensor(grey)
# # #
# # # # ----------------------------------------------------------
# lidar = Lidar(my_agent.base_platform, normalize=False, invisible_elements=my_agent.parts, fov=180, resolution=128, max_range=400)
# my_agent.add_sensor(lidar)
# # # # #
# depth = Proximity(my_agent.base_platform, normalize=False, invisible_elements=my_agent.parts, fov=100, resolution=64, max_range=400)
# my_agent.add_sensor(depth)
# # # # #
# touch = Touch(my_agent.base_platform, normalize=True, invisible_elements=my_agent.parts)
# my_agent.add_sensor(touch)
# #
# # # ----------------------------------------------------------
# sem_ray = SemanticRay(my_agent.base_platform, invisible_elements=my_agent.parts, remove_duplicates=False, fov=90)
# my_agent.add_sensor(sem_ray)
# # #
# sem_cones = SemanticCones(my_agent.base_platform, invisible_elements=my_agent.parts, normalize=True, remove_duplicates=False)
# my_agent.add_sensor(sem_cones)
# # #
# # # ----------------------------------------------------------
# td = TopdownSensor(my_agent.base_platform, invisible_elements=my_agent.parts, normalize=True, only_front=True, fov=180)
# my_agent.add_sensor(td)
# #
# fi = FullPlaygroundSensor( size_playground=my_playground.size, resolution=64)
# my_agent.add_sensor(fi)

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

my_playground.add_agent(my_agent, allow_overlapping=False)
# my_playground.add_agent(dummy, initial_coordinates=((100, 50), 0))

# we use the option screen=True to use a keyboard controlled agent later on.
engine = Engine(playground=my_playground, screen=True, debug=False)

# Run all
t_start = time.time()
engine.run(update_screen=True, print_rewards=True)
t_stop = time.time()
print(10000 / (t_stop - t_start))

# my_playground.remove_agent(my_agent)
# rgb = RgbCamera(my_agent.base_platform, invisible_elements=my_agent.parts, resolution=64, max_range=500)
# my_agent.add_sensor(rgb)
# my_playground.add_agent(my_agent)

for i in range(5):
    # Run step by step and display
    engine.reset()
    engine.run(update_screen=True)

engine.reset()

# my_agent.position = (100, 150)
# pylint: skip-file

while engine.game_on:

    engine.update_screen()

    actions = {}
    for agent in engine.agents:
        actions[agent] = agent.controller.generate_actions()

    engine.multiple_steps(actions, 2)
    engine.update_observations()

    cv2.imshow(
        'agent',
        engine.generate_agent_image(my_agent,
                                    layout=(('sensors', 'playground'),
                                            'actions')))
    cv2.waitKey(25)

# cv2.destroyAllWindows()
# engine.reset()
# while engine.game_on:
#     engine.run(steps = 100, update_screen=False)
#     engine.update_screen()
#     print(engine._elapsed_time)
