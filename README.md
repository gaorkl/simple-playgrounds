# Welcome to simple-playgrounds

The goal of this project is to provide easy-to-use, fast and flexible
simulation environments for research in Deep Reinforcement Learning and Artificial Intelligence.
This simulator offers test beds which can be easily tuned to the need of the researcher.
It bridges the gap between simple and efficient grid environments, and complex and challenging 3D environments.

The playgrounds are 2D environments where agents can move around and interact with entities.
The game engine deals with simple physics, such as collision and friction.
Agents can act through continuous movements and discrete interactive actions.
They can perceive the scene with realistic first-person view sensors, top-dow vew sensors, and 
semantic sensors.

![Alt Text](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/assets/spg.gif)

This simulator is easy to handle. It allows very fast design of AI experiments
and runs experiments very quickly.

If you are interested in using this simulator for your research, please use the following reference:

```
@misc{Simple-Playgrounds,
  author = {Garcia Ortiz, Michael and Caselles-Dupre Hugo and Annabi, Louis},
  title = {Simple-Playgrounds},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/mgarciaortiz/simple-playgrounds}},
}
```

# Installation

Before installing, you might have to install libsdl1.2-dev and pygame manually.

Once these dependencies are installed, you can install simple-playgrounds using pip.
A pip package is available and regularly updated:

`pip3 install simple-playgrounds`


# Tutorials

We provide a series of small tutorials to illustrate the capabilities
of simple-playgrounds. We suggest to run them locally to benefit from
the keyboard control of the agents.

Alternatively, you can run the colab versions, which are less interactive.
(not ready yet)

[01 - Welcome to simple-playgrounds](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/01_Intro.ipynb)

[02 - Learn to build playgrounds](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/02_Playgrounds_and_positions.ipynb)

[03 - Add elements to your playground](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/03_SceneElements.ipynb)

[04 - Modify the appearance of elements](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/04_Textures.ipynb)

[05 - Fields elements](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/05_Fields.ipynb)

[06 - Using agents and sensors](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tutorials/jupyter/06_Agents.ipynb)

We advise to run the notebook locally, so that more advanced display options are available.

# Structure of a playground

A playground is described using a carthesian coordinate system. 
Each element has a position (x,y, &theta), 
with x along the horizontal axis, y along the vertical axis, and
theta the orientation, aligned on horizontal axis.

A playground has a size [width, length], with the width along x axis, 
and length along y axis

When applicable, the length of a scene element follows the element's x axis.

# Acknowledgements

The first version of the simulator was called Flatland, and was designed by 
Hugo Caselles-Dupre, Louis Annabi, Oksana Hagen and Michael Garcia Ortiz.

The new version was developped by Hugo Caselles-Dupre, Louis Annabi and Michael Garcia Ortiz.

We would like to thank Clement Moulin-Frier and Younes Rabii for their helpful 
suggestions and their contributions to the new version of the simulator.

