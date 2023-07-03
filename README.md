# Welcome to SimplePlaygrounds

SimplePlaygrounds (SPG) is an easy-to-use, fast and flexible
simulation environment for research in Deep Reinforcement Learning and Artificial Intelligence.
This simulator proposes a huge diversity of environments for embodied agents learning.
It bridges the gap between simple and efficient grid-word environments, and complex and challenging 3D environments.

The playgrounds are 2D environments where agents can move around and interact with scene elements and other agents.
The game engine is based on [Pymunk](http://www.pymunk.org), and allows very fine-grained physical interactions between elements
of SPG.
[Arcade](https://api.arcade.academy/en/latest/), is used to render the playground, and its integration of OpenGL shaders
is used to calculate first-person sensors at high speed.

If you are using Simple Playgrounds in your research, please cite us!

```
@misc{SimplePlaygrounds,
  author = {Garcia Ortiz, Michael and Jankovics, Vince},
  title = {Simple-Playgrounds},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/gaorkl/simple-playgrounds}},
}
```

## Table of Contents

- [Installation](#installation)
- [Demo](#demo)
- [Examples and Tutorials](#examples-and-tutorials)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact](#contact)

## Installation

Detailed installation instructions. Include any prerequisites and then the command or commands to install your project.

```bash
pip install spg
```

## Demo

```python
import spg
```

WIP

## Examples and Tutorials

Link to your tutorials here.

- [Tutorial 1](./tutorials/tutorial1.md)
- [Tutorial 2](./tutorials/tutorial2.md)
- [Tutorial 3](./tutorials/tutorial3.md)

WIP

## Contributing

Pull Requests welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for more information.


## License

This project is licensed under the terms of the [MIT license](./LICENSE).

## Credits

The first version of the simulator was called Flatland, and was designed by
Hugo Caselles-Dupre, Louis Annabi, Oksana Hagen and Michael Garcia Ortiz.

This version was developed by Vince Jankovics and Michael Garcia Ortiz.

## Contact

If you have any questions, please contact us on github.
