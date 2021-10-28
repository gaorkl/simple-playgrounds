# Welcome to simple-playgrounds

Simple-Playgrounds (SPG) is an easy-to-use, fast and flexible
simulation environment for research in Deep Reinforcement Learning and Artificial Intelligence.
This simulator proposes a huge diversity of environments for embodied agents learning
through physical interactions.
It bridges the gap between simple and efficient grid environments, and complex and challenging 3D environments.

The playgrounds are 2D environments where agents can move around and interact with scene elements.
The game engine, based on [Pymunk](http://www.pymunk.org) and [Pygame](https://www.pygame.org), deals with simple physics, such as collision and friction.
Agents can act through continuous movements and discrete interactive actions.
They perceive the scene with realistic first-person view sensors, top-down view sensors, and 
semantic sensors.

![Alt Text](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/assets/spg.gif)

This simulator is easy to handle, and very flexible. It allows very fast design of AI experiments
and runs experiments very quickly.

We hope that you can make use of this simulator for your research.
If you publish your work based on this simulator, please use the following reference:

```
@misc{Simple-Playgrounds,
  author = {Garcia Ortiz, Michael and Jankovics, Vince and Caselles-Dupre, Hugo and Annabi, Louis},
  title = {Simple-Playgrounds},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/mgarciaortiz/simple-playgrounds}},
}
```

# Installation

Before installing Simple-Playgrounds, you might need to install libsdl1.2-dev and Pygame manually.

Once these dependencies are installed, you can install simple-playgrounds using pip.
A pip package is available and regularly updated:

`pip3 install simple-playgrounds`

# Tutorials

We provide a series of small tutorials to illustrate the capabilities
of Simple-Playgrounds. We suggest running them locally to benefit from
the keyboard control of the agents.

[01 - Welcome to simple-playgrounds](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/01_Intro.ipynb)

[02 - Learn to build playgrounds](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/02_Playgrounds_and_positions.ipynb)

[03 - Add elements to your playground](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/03_SceneElements.ipynb)

[04 - Modify the appearance of elements](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/04_Textures.ipynb)

[05 - Spawners elements](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/05_Spawners.ipynb)

[06 - Using agents and sensors](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/06_Agents.ipynb)

We advise to run the notebook locally, so that more advanced display options are available.

# Structure of the simulator

## Agents

Agents are composed of different body parts attached to a Base.
Different bases are available, each of them with different actuators.

The actuators controlling the base and body parts are managed by a controller.
The controller can be:
- Random: each actuator is set randomly at every timestep. 
- Keyboard: the agent is controlled by pressing keys on the Keyboard. 
- External: used to set the actions from outside of the simulators (used in RL)

Agents perceive their surroundings through a large collection of first-person view sensors:
- RGB Camera / Grey Level Camera
- Lidar 
- Touch Sensor
- Top-down view
- Semantic Sensors (Rays or Cones)

Any number of sensors can be added to the agent. The sensors are parameterizable in terms of 
field of view, range, and resolution.

### Noise

Sensors as well as Actuators can be noisy.

## Playground

Agents act and perceive in a Playground. 
A playground is composed of scene elements, which can be fixed or movable.
An agent can grasp, eat, activate or absorb certain scene elements.
Depending on their nature, particular scene elements will provide reward to the agent 
interacting with them.

### Coordinate System

A playground is described using a Cartesian coordinate system. 
Each element has a position (x,y, &theta), 
with x along the horizontal axis, y along the vertical axis, and
theta the orientation, aligned on the horizontal axis.

A playground has a size [width, length], with the width along x-axis, 
and length along y-axis

When applicable, the length of a scene element follows the element's x-axis.

A playground is a collection of scene elements, and therefore can be very easily scripted.

## Game Engine

Agents enter a Playground, and start acting and perceiving within this environment.
The perception/action loop is managed by a Game Engine.

# Application of SPG in different Research fields

The classical use of SPG is Reinforcement Learning. You can build simple to very complex environments
that look into classical challenges of RL.
The diversity and speed of SPG allows to experiment on:
- Continual learning and Transfer Learning: Move the agent from Playground to Playground.
- Exploration: Get the key to open the door to get the other key to open the chess that will give you the reward.

SPG allows you to address the problematics of other fields related to RL:
- MARL: why not put several agents in the environments?
- Curriculum learning: Send agents to Playgrounds of increasing difficulty
- Procedural Generation: Automatically create just the right Playground.
- Representation learning and commonsense knowledge.

Because of its flexibility, and the numerous sensors and actuators, SPG allows to test for:
- generalization of your approach
- resistance to noise, and variations of sensor types
- reproducibility

# Acknowledgements

The first version of the simulator was called Flatland, and was designed by 
Hugo Caselles-Dupre, Louis Annabi, Oksana Hagen and Michael Garcia Ortiz.

The new version was developed by Vince Jankovics, Hugo Caselles-Dupre, Louis Annabi and Michael Garcia Ortiz.

We would like to thank Clement Moulin-Frier and Younes Rabii for their helpful 
suggestions and their contributions to the new version of the simulator.

