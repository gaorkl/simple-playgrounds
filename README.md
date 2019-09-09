# flatland
New version of flatland.


# TODO:
- Replace Ctr+q with clean exiting which doesnt require a pygame display
- Add a cost of activation for actionable objects ?
- create a function for random position of agent / produced objects
- harmonize coordinate system and shapes of envir
- teleport agent (for alban)
- implement simulation steps, size_envir, multithreading

# TODO entities:
- create key for door (graspable + door mechanism)
- create visible / invisible fire areas
- fire objects
- initialize textures
- modify default config, so that it can be specified by user

# TODO agents:
- add rbgd, depth, rbg-tamed 
- Modify metabolism, harmonize name for head_velocity, head_speed, ... and computation of energy

# TODO Gui
- one window per agent with sensors and reward
- integration with ipynb
- harmonize definition of x, y , angle, width, height

# TODO RL:
- end zone
- reset environment
- object for end of episode (wall, ball)
- puck object, with radius, which gives negative reward

# TODO entities:
- key lock and key to open door
- areas with kill zone
- agents with kill zones
- end zone
- object to zone for reward
- moving objects along with a trajectory
- moving objects with constant speed vector