# flatland
New version of flatland.

# TODO General:
- documentation
- safeguard
- jupyter notebook / colab compatible
- install pipy and pip
- visualization agent, fpv, topdown view
- harmonize view (carthesian) and coordinates
- video recording


# Game engine
- keep textures when reset: create reset_pg, reset_entities, ...
- config file
- start position: random in area (circle, square, gaussian), random pick in list positions, random pick in list areas
- fixed, list_fixed, area, list_areas
- each playground should suggest starting positions
- also random position for object placements
- basic environments
- change default parameters and use config / yaml ?
- teleport agent to position (and set all agent speeds to zero)
- add cost of activation / grasp for objects

# Todo PG:
- Scene layouts linear, array, random maze
- test pg with all items
- walls of random colors / one color per wall 
- random position: weighted list of areas
- check if position valid

# TODO RL:
- wrapper openai & gym
- wrapper library state representation
- parallel vector agents and environments


# TODO:
- Replace Ctr+q with clean exiting which doesnt require a pygame display
- Add a cost of activation for actionable objects ?

# TODO agents:
- add rbgd, depth, rbg-limited_view, top-down
- Modify metabolism, harmonize name for head_velocity, head_speed, ... and computation of energy
- focus on single agent
- merge sm-agent

# TODO Gui
- one window per agent with sensors and reward
- integration with ipynb
