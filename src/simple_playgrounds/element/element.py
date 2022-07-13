"""
Module that defines Base Class SceneElement
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from simple_playgrounds.entity.physical import PhysicalEntity


class SceneElement(PhysicalEntity, ABC):
    def __init__(self, **entity_params):
        super().__init__(**entity_params)


class InteractiveElement(SceneElement, ABC):
    pass

class Teleporter(InteractiveElement):
    pass
