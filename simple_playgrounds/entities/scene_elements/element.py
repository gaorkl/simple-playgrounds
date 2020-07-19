"""
Module that defines Base Class SceneElement
"""

from abc import ABC
import os
import yaml

from simple_playgrounds.entities.entity import Entity


class SceneElement(Entity, ABC):
    """
    A SceneElement can have interactive properties, passive properties.

    Attributes:
        absorbable: Disappears upon contact with an Agent.
        edible: Can be eaten by an agent.
        movable: Can move.
        graspable: Can be grasped by an agent.
        timed: Behavior depends on timer.
        terminate_upon_contact: Terminates the episode upon contact with an Agent.
    """

    absorbable = False
    edible = False

    movable = False
    follows_waypoints = False
    graspable = False

    timed = False

    terminate_upon_contact = False

    def __init__(self, initial_position=None, **kwargs):

        self.graspable = kwargs.get('graspable', self.graspable)
        self.movable = kwargs.get('movable', self.movable)

        if self.graspable:
            self.interactive = True
            self.movable = True

        Entity.__init__(self, initial_position=initial_position, **kwargs)

    @staticmethod
    def _parse_configuration(entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[key]
