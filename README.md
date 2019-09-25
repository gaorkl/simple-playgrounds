# flatland
New version of flatland.

# TODO:
- start position: random in area (circle, square, gaussian), random pick in list positions, random pick in list areas
- fixed, list_fixed, area, list_areas
- each playground should suggest starting positions
- also random position for object placements
- basic environments
- change default parameters and use config / yaml ?
- teleport agent to position (and set all agent speeds to zero)
- add cost of activation / grasp for objects

# TODO RL:
- wrapper openai & gym
- wrapper library state representation

# TODO:
- Replace Ctr+q with clean exiting which doesnt require a pygame display
- Add a cost of activation for actionable objects ?


# TODO agents:
- add rbgd, depth, rbg-limited_view, top-down
- Modify metabolism, harmonize name for head_velocity, head_speed, ... and computation of energy

# TODO Gui
- one window per agent with sensors and reward
- integration with ipynb
