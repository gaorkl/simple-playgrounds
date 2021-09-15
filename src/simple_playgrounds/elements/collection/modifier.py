"""
Scene elements that interact with an agent when they are in range.
Passive Scene Elements do not require action from an agent.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union

from ...common.entity import Entity
from ...common.definitions import ElementTypes, CollisionTypes
from ...configs.parser import parse_configuration
from ...elements.element import SceneElement
from ...agents.communication import CommunicationDevice
from ...agents.sensors.sensor import SensorDevice


class ModifierElement(SceneElement, ABC):
    """ Base Class for Modifier Elements.
    Modifier Elements modify properties of other elements."""
    def __init__(self, **entity_params):

        SceneElement.__init__(self,
                              visible_shape=False,
                              invisible_shape=True,
                              **entity_params)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.MODIFIER

    @abstractmethod
    def activate(self, activated):
        ...


class CommBlackoutZone(ModifierElement, ABC):

    def __init__(self,
                 **entity_params):

        default_config = parse_configuration('element_modifier', ElementTypes.COMM_BLACKOUT)
        entity_params = {**default_config, **entity_params}

        super().__init__(**entity_params)

    def activate(self, comm: CommunicationDevice):

        if isinstance(comm, CommunicationDevice):
            comm.disable()


class SensorBlackoutZone(ModifierElement, ABC):

    def __init__(self,
                 **entity_params):

        default_config = parse_configuration('element_modifier', ElementTypes.SENSOR_BLACKOUT)
        entity_params = {**default_config, **entity_params}

        super().__init__(**entity_params)

    def activate(self, sensor: SensorDevice):

        if isinstance(sensor, SensorDevice):
            sensor.disable()
