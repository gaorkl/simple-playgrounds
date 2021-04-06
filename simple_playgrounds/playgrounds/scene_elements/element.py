"""
Module that defines Base Class SceneElement
"""

from abc import ABC

from simple_playgrounds.entity import Entity


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

    overlapping=None

    terminate_upon_contact = False

    def __init__(self, **kwargs):

        self.graspable = kwargs.get('graspable', self.graspable)
        self.movable = kwargs.get('movable', self.movable)

        if self.graspable:
            self.interactive = True
            self.movable = True

        if self.movable:
            self.background = False

        Entity.__init__(self, **kwargs)
