""" Module implementing Controllers.
Controllers are used to generate commands to control the actuators of an agent.
"""
import random
from abc import ABC, abstractmethod
from typing import List, Dict

import pygame

from .actuators import ActuatorDevice, DiscreteActuator, ContinuousActuator
from simple_playgrounds.common.definitions import KeyTypes


class Controller(ABC):
    """ Base Class for Controllers.
    """
    def __init__(self):

        self.require_key_mapping: bool = False
        self._controlled_actuators: List[ActuatorDevice] = []

    @abstractmethod
    def generate_actions(self) -> Dict[ActuatorDevice, float]:
        """ Generate actions for each actuator of an agent,
        Returns a dictionary of actuators and associated action value.
        """

    def generate_null_actions(self) -> Dict[ActuatorDevice, float]:
        """
        Generate dictionary of actuators and null actions.
        All actions are set to zero.
        """
        commands = {}
        for actuator in self.controlled_actuators:
            commands[actuator] = actuator.default_value

        return commands

    @property
    def controlled_actuators(self) -> List[ActuatorDevice]:
        return self._controlled_actuators

    @controlled_actuators.setter
    def controlled_actuators(self, actuators: List[ActuatorDevice]):
        self._controlled_actuators = actuators


class External(Controller):
    """
    This controller is used when actions are decided from outside of the simulator.
    E.g. this class can be used with RL algorithms.
    """
    def generate_actions(self):
        pass


class Dummy(Controller):
    """
    This controller is used when actions are decided from outside of the simulator.
    E.g. this class can be used with RL algorithms.
    """
    def generate_actions(self):
        return self.generate_null_actions()


class RandomDiscrete(Controller):
    """
    A random controller generate random commands.
    If the actuator is continuous, it picks the actions in:
     - {-1, 0, 1} if the actuator is centered
     - {0, 1} is not centered.
    If the actuator is discrete, it picks a random action in the set of available actions.
    """
    def generate_actions(self):

        commands = {}

        for actuator in self.controlled_actuators:

            if isinstance(actuator, DiscreteActuator):
                act_value = random.choice([0, 1])

            elif isinstance(actuator, ContinuousActuator):

                if actuator.centered:
                    act_value = random.choice([-1, 0, 1])
                else:
                    act_value = random.choice([0, 1])

            else:
                raise ValueError("Actuator type not recognized")

            commands[actuator] = act_value

        return commands


class RandomContinuous(Controller):
    """
    A random controller generate random commands.
    If the actuator is continuous, it picks the action using a uniform distribution.
    If the actuator is discrete (binary), it picks a random action.
    """
    def generate_actions(self):

        commands = {}

        for actuator in self.controlled_actuators:

            act_value = actuator.default_value

            if isinstance(actuator, DiscreteActuator):
                act_value = random.choice([0, 1])

            elif isinstance(actuator, ContinuousActuator):

                if actuator.centered:
                    act_value = random.uniform(-1, 1)
                else:
                    act_value = random.uniform(0, 1)

            else:
                raise ValueError("Actuator type not recognized")

            commands[actuator] = act_value

        return commands


class Keyboard(Controller):
    """
    Keyboard controller require that a keymapping is defined in the agent.
    The keymapping should be assigned to the controller.
    """
    def __init__(self):

        super().__init__()

        self.require_key_mapping = True
        self.key_map = None

        self.press_once = []
        self.press_hold = []

        self.hold = []

    def discover_key_mapping(self):
        """ Key mapping that links keyboard strokes with a desired action."""

        self.key_map = {}

        for actuator in self.controlled_actuators:

            if actuator.has_key_mapping:

                for key, (behavior, value) in actuator.key_map.items():

                    if key in self.key_map:
                        raise ValueError("Key assigned twice")

                    self.key_map[key] = (actuator, behavior, value)

    def generate_actions(self):

        # pylint: disable=undefined-variable

        all_key_pressed = pygame.key.get_pressed()

        pressed = []
        for key, _ in self.key_map.items():
            if all_key_pressed[key] == 1:
                pressed.append(key)

        for key_pressed in self.press_hold:
            if key_pressed not in pressed:
                self.press_hold.remove(key_pressed)

        for key_pressed in self.press_once:
            if key_pressed not in pressed:
                self.press_once.remove(key_pressed)

        commands = self.generate_null_actions()

        for key_pressed in pressed:

            actuator, behavior, value = self.key_map[key_pressed]

            if behavior == KeyTypes.PRESS_HOLD:
                commands[actuator] = value

                if key_pressed not in self.press_hold:
                    self.press_hold.append(key_pressed)

            if behavior == KeyTypes.PRESS_ONCE and key_pressed not in self.press_once:
                commands[actuator] = value
                self.press_once.append(key_pressed)

        return commands

    @property
    def controlled_actuators(self):
        return self._controlled_actuators

    @controlled_actuators.setter
    def controlled_actuators(self, contr):
        self._controlled_actuators = contr
        self.discover_key_mapping()
