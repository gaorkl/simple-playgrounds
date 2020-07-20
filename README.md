# Intro

Early release of the simulator simple-playgrounds

First tutorial:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](  https://colab.research.google.com/github/mgarciaortiz/simple-playgrounds/blob/master/tutorials/example.ipynb)

We advise to run the notebook locally, so that more advanced display options are available.

# Install

pip3 install simple-playgrounds

# Coordinates, shapes of environments

Carthesian coordinate system:
- x along the horizontal axis
- y along the vertical axis
- theta orientation, aligned on horizontal axis


Environment:
- size: [width, length]
- width along x axis, length along y axis

Entities:
- position x, y, phi
- phi orientation
- length along axis of phi = 0
- width perpendicular to axis phi = 0

Examples:

[Building a playground](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/simple_playgrounds/playgrounds/collection/test/test_scene_elements.py)

[Building an agent and adding sensors](https://github.com/mgarciaortiz/simple-playgrounds/blob/master/tests/test_sensors.py)

