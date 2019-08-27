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

# TODO agents:
- for now, every sensor computed independently. But polar need only to be computed once
- modify sensors: default rgb and touch sensor params.
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
