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


# API

Simple PLaygrounds follows the gymnasium environment definitions.



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

# Acknowledgements

The first version of the simulator was called Flatland, and was designed by
Hugo Caselles-Dupre, Louis Annabi, Oksana Hagen and Michael Garcia Ortiz.

The new version was developed by Vince Jankovics, Hugo Caselles-Dupre, Louis Annabi and Michael Garcia Ortiz.

We would like to thank Clement Moulin-Frier and Younes Rabii for their helpful
suggestions and their contributions to the new version of the simulator.

