# 2D playgrounds for AI

Welcome to simple-playgrounds, a library for designing simple playgrounds.

The playgrounds are 2D environments equipped with physics (collision, friction)
Agents can act through continuous movements and discrete interactive actions.
They perceive with realistic first-person view sensors, top-dow vew sensors, and 
semantic sensors.

This simulator is easy to handle. It allows very fast design of AI experiments
and runs experiments very quickly.

# Installation

A pip package is available and regularly updated:

`pip3 install simple-playgrounds`

Early release of the simulator simple-playgrounds

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
Each element has a position (x,y,$$\Theta$$), 
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

